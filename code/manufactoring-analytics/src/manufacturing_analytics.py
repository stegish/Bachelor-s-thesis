import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pymongo import MongoClient
import mongomock
from typing import List, Dict, Any
import csv
import json
from collections import defaultdict


class ManufacturingAnalytics:
    def __init__(self, mongo_uri: str, orders_db: str, process_db: str | None = None):
        """Initialize the analytics service with MongoDB connection.

        - `orders_db` contains the production orders.
        - `process_db` stores the machine cluster info. If `process_db` is None,
          we use `orders_db` for both collections.
        """
        self.client = MongoClient(mongo_uri)

        self.orders_db = self.client[orders_db]
        self.orders_collection = self.orders_db["newOrdini"]

        self.process_db = self.client[process_db] if process_db else self.orders_db
        self.machines_collection = self.process_db["macchinari"]

    @staticmethod
    def _parse_date(field: Any) -> Any:
        """
        Accepts either:
          1) a Python `datetime` (in which case we just return it),
          2) a MongoDB‐style dict {"$date": {"$numberLong": "..."}}, or
          3) None/empty.
        Returns a `datetime` or `None`.
        """
        if isinstance(field, datetime):
            return field

        if not field:
            return None

        if isinstance(field, dict):
            date_obj = field.get("$date", None)
            if isinstance(date_obj, dict):
                millis = date_obj.get("$numberLong", None)
                if millis is not None:
                    # convert from milliseconds to seconds‐timestamp
                    return datetime.fromtimestamp(int(millis) / 1000)

        return None

    @staticmethod
    def _parse_number_int(field_value: Any) -> int:
        """
        Accepts either:
          1) a dict like {"$numberInt": "5"},
          2) a raw int (or string that can be cast to int),
          3) None.
        Returns an int (defaulting to 0 if missing or None).
        """
        if isinstance(field_value, dict):
            return int(field_value.get("$numberInt", 0))
        elif field_value is None:
            return 0
        else:
            return int(field_value)

    def extract_phase_metrics(self, orders: List[Dict]) -> pd.DataFrame:
        """Extract detailed phase‐level metrics from the list of `orders`."""
        phase_data: List[Dict[str, Any]] = []

        for order in orders:
            order_id = order.get("orderId", "")
            order_status = self._parse_number_int(order.get("orderStatus", None))
            order_quantity = self._parse_number_int(order.get("quantity", None))

            phases = order.get("Phases", [])
            for phase in phases:
                # 1) Pull out numeric fields via _parse_number_int
                raw_cycle_time = phase.get("cycleTime", None)
                raw_real_time = phase.get("phaseRealTime", None)
                raw_declared_qty = phase.get("declaredQuantity", None)

                cycle_time = self._parse_number_int(raw_cycle_time)
                phase_real_time = self._parse_number_int(raw_real_time)
                declared_quantity = (
                    self._parse_number_int(raw_declared_qty) if raw_declared_qty is not None else 0
                )

                # 2) Operators → comma‐joined string + count
                operators_list = phase.get("operators", [])
                operator_str = ",".join(operators_list)
                operator_count = len(operators_list)

                # 3) Build the base record
                phase_record: Dict[str, Any] = {
                    "order_id": order_id,
                    "order_status": order_status,
                    "order_quantity": order_quantity,
                    "phase_id": phase.get("phaseId", ""),
                    "phase_name": phase.get("phaseName", ""),
                    "phase_status": self._parse_number_int(phase.get("phaseStatus", None)),
                    "cycle_time": cycle_time,
                    "phase_real_time": phase_real_time,
                    "declared_quantity": declared_quantity,
                    "operators": operator_str,
                    "operator_count": operator_count,
                }

                # 4) Parse all four possible date fields
                #    (queueInsertDate, queueRealInsertDate, finishDate, realFinishDate)
                phase_record["queue_insert_date"] = self._parse_date(
                    phase.get("queueInsertDate", None)
                )
                phase_record["queue_real_insert_date"] = self._parse_date(
                    phase.get("queueRealInsertDate", None)
                )
                phase_record["planned_finish_date"] = self._parse_date(
                    phase.get("finishDate", None)
                )
                phase_record["real_finish_date"] = self._parse_date(
                    phase.get("realFinishDate", None)
                )

                # 5) Calculate queue‐delay hours if both dates are present
                if (
                    phase_record["queue_insert_date"]
                    and phase_record["queue_real_insert_date"]
                ):
                    delta = (
                        phase_record["queue_real_insert_date"]
                        - phase_record["queue_insert_date"]
                    ).total_seconds() / 3600
                    phase_record["queue_delay_hours"] = delta
                else:
                    phase_record["queue_delay_hours"] = None

                # 6) Calculate finish‐delay hours if both planned + actual finish exist
                if (
                    phase_record["planned_finish_date"]
                    and phase_record["real_finish_date"]
                ):
                    delta = (
                        phase_record["real_finish_date"]
                        - phase_record["planned_finish_date"]
                    ).total_seconds() / 3600
                    phase_record["finish_delay_hours"] = delta
                else:
                    phase_record["finish_delay_hours"] = None

                # 7) Actual duration (minutes) = difference between queue_real_insert_date and real_finish_date
                if (
                    phase_record["queue_real_insert_date"]
                    and phase_record["real_finish_date"]
                ):
                    delta = (
                        phase_record["real_finish_date"]
                        - phase_record["queue_real_insert_date"]
                    ).total_seconds() / 60
                    phase_record["actual_duration_minutes"] = delta
                else:
                    phase_record["actual_duration_minutes"] = None

                # 8) Planned duration = cycle_time × declared_quantity (if declared_quantity > 0),
                #    otherwise just cycle_time
                if declared_quantity > 0:
                    phase_record["planned_duration_minutes"] = cycle_time * declared_quantity
                else:
                    phase_record["planned_duration_minutes"] = cycle_time

                phase_data.append(phase_record)

        return pd.DataFrame(phase_data)

    def calculate_machine_metrics(
        self, phase_df: pd.DataFrame, machines: List[Dict]
    ) -> pd.DataFrame:
        """Calculate machine‐level metrics (utilization, queue stats, etc.)."""
        machine_metrics: List[Dict[str, Any]] = []

        for machine in machines:
            machine_name = machine.get("name", "")
            is_active = machine.get("macchinarioActive", False)

            # Here queueTargetTime is still a dict {"$numberInt": "..."} or raw int
            queue_target_time = self._parse_number_int(
                machine.get("queueTargetTime", None)
            )

            current_queue_length = len(machine.get("tablet", []))

            # Filter the phase_df down to records where phase_name == machine_name
            if "phase_name" in phase_df.columns:
                machine_phases = phase_df[phase_df["phase_name"] == machine_name]
            else:
                machine_phases = pd.DataFrame()

            if not machine_phases.empty:
                metrics: Dict[str, Any] = {
                    "machine_name": machine_name,
                    "is_active": is_active,
                    "queue_target_time": queue_target_time,
                    "current_queue_length": current_queue_length,
                    "total_phases_processed": len(machine_phases),
                    "completed_phases": len(
                        machine_phases[machine_phases["phase_status"] == 4]
                    ),
                    "in_progress_phases": len(
                        machine_phases[
                            machine_phases["phase_status"].isin([1, 2, 3])
                        ]
                    ),
                    "avg_cycle_time": machine_phases["cycle_time"].mean(),
                    "avg_actual_duration": machine_phases[
                        "actual_duration_minutes"
                    ].mean(),
                    "avg_queue_delay": machine_phases["queue_delay_hours"].mean(),
                    "avg_finish_delay": machine_phases["finish_delay_hours"].mean(),
                    "total_quantity_processed": machine_phases[
                        "declared_quantity"
                    ].sum(),
                    # Unique operators across all matched phases
                    "unique_operators": len(
                        set(
                            ",".join(
                                machine_phases["operators"].fillna("")
                            ).split(",")
                        )
                    ),
                }

                # Efficiency = (avg_cycle_time / avg_actual_duration) × 100
                if (
                    metrics["avg_cycle_time"] > 0
                    and not pd.isna(metrics["avg_actual_duration"])
                ):
                    metrics["efficiency_percentage"] = (
                        metrics["avg_cycle_time"] / metrics["avg_actual_duration"]
                    ) * 100
                else:
                    metrics["efficiency_percentage"] = None

                # Utilization (assume 8‐hour workday):
                #   total_working_minutes = (#days_between_first_and_last_finish) × 8 × 60
                #   actual_minutes = sum(actual_duration_minutes)
                #   utilization = actual_minutes / total_working_minutes
                completed = machine_phases[
                    machine_phases["real_finish_date"].notna()
                ]
                if not completed.empty:
                    first_start = machine_phases["queue_real_insert_date"].min()
                    last_finish = machine_phases["real_finish_date"].max()
                    date_range = last_finish - first_start
                    working_days = date_range.days
                    if working_days > 0:
                        total_working_minutes = working_days * 8 * 60
                        total_actual_minutes = machine_phases[
                            "actual_duration_minutes"
                        ].sum()
                        metrics["utilization_percentage"] = (
                            total_actual_minutes / total_working_minutes
                        ) * 100
                    else:
                        metrics["utilization_percentage"] = None
                else:
                    metrics["utilization_percentage"] = None

                machine_metrics.append(metrics)

        return pd.DataFrame(machine_metrics)

    def generate_order_timeline(self, orders: List[Dict]) -> pd.DataFrame:
        """Generate timeline data for each order (lead times, delays, on_time, etc.)."""
        timeline_data: List[Dict[str, Any]] = []

        for order in orders:
            order_id = order.get("orderId", "")
            article_code = order.get("codiceArticolo", "")
            product_family = order.get("famigliaDiProdotto", "")

            quantity = self._parse_number_int(order.get("quantity", None))
            priority = self._parse_number_int(order.get("priority", None))
            order_status = self._parse_number_int(order.get("orderStatus", None))

            # Reuse the same _parse_date helper
            insert_date = self._parse_date(order.get("orderInsertDate", None))
            start_date = self._parse_date(order.get("orderStartDate", None))
            deadline = self._parse_date(order.get("orderDeadline", None))
            real_finish_date = self._parse_date(order.get("realOrderFinishDate", None))

            record: Dict[str, Any] = {
                "order_id": order_id,
                "article_code": article_code,
                "product_family": product_family,
                "quantity": quantity,
                "priority": priority,
                "order_status": order_status,
                "insert_date": insert_date,
                "start_date": start_date,
                "deadline": deadline,
                "real_finish_date": real_finish_date,
            }

            # Lead time in days = (real_finish_date − insert_date).days, if both exist
            if insert_date and real_finish_date:
                record["lead_time_days"] = (real_finish_date - insert_date).days
            else:
                record["lead_time_days"] = None

            # Delay in days & on_time flag
            if deadline and real_finish_date:
                delay_days = (real_finish_date - deadline).days
                record["delay_days"] = delay_days
                record["on_time"] = delay_days <= 0
            else:
                record["delay_days"] = None
                record["on_time"] = None

            timeline_data.append(record)

        return pd.DataFrame(timeline_data)

    def generate_queue_analysis(self, phase_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze queue patterns & identify bottlenecks.

        Groups by phase_name and computes:
          - avg / std / max queue_delay_hours
          - total_jobs (count of phases)
          - total_quantity (sum of declared_quantity)
          - is_bottleneck = True if avg_queue_delay > (mean + std) over all machines
        """
        if phase_df.empty or "phase_name" not in phase_df.columns:
            return pd.DataFrame(
                columns=[
                    "phase_name",
                    "avg_queue_delay",
                    "queue_delay_std",
                    "max_queue_delay",
                    "total_jobs",
                    "total_quantity",
                    "is_bottleneck",
                ]
            )

        queue_metrics = (
            phase_df.groupby("phase_name")
            .agg(
                {
                    "queue_delay_hours": ["mean", "std", "max"],
                    "phase_id": "count",
                    "declared_quantity": "sum",
                }
            )
            .round(2)
        )
        queue_metrics.columns = [
            "avg_queue_delay",
            "queue_delay_std",
            "max_queue_delay",
            "total_jobs",
            "total_quantity",
        ]
        queue_metrics = queue_metrics.reset_index()

        # Compute global mean + std on avg_queue_delay, then mark bottlenecks
        global_mean = queue_metrics["avg_queue_delay"].mean()
        global_std = queue_metrics["avg_queue_delay"].std()
        threshold = global_mean + global_std

        queue_metrics["is_bottleneck"] = (
            queue_metrics["avg_queue_delay"] > threshold
        )

        return queue_metrics

    def generate_operator_performance(self, phase_df: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze each operator’s performance metrics:
          - total_phases (count of phases they appeared in)
          - avg_cycle_time
          - avg_actual_duration
          - total_quantity
          - efficiency = (avg_cycle_time / avg_actual_duration) * 100
        """
        operator_data: List[Dict[str, Any]] = []

        for _, row in phase_df.iterrows():
            operators = row.get("operators", "")
            if operators:
                for operator in operators.split(","):
                    operator = operator.strip()
                    if not operator:
                        continue
                    operator_data.append(
                        {
                            "operator": operator,
                            "phase_name": row["phase_name"],
                            "cycle_time": row["cycle_time"],
                            "actual_duration": row["actual_duration_minutes"],
                            "declared_quantity": row["declared_quantity"],
                            "phase_status": row["phase_status"],
                        }
                    )

        operator_df = pd.DataFrame(operator_data)
        if operator_df.empty:
            return pd.DataFrame()

        operator_metrics = (
            operator_df.groupby("operator")
            .agg(
                {
                    "phase_name": "count",
                    "cycle_time": "mean",
                    "actual_duration": "mean",
                    "declared_quantity": "sum",
                }
            )
            .round(2)
        )
        operator_metrics.columns = [
            "total_phases",
            "avg_cycle_time",
            "avg_actual_duration",
            "total_quantity",
        ]
        operator_metrics["efficiency"] = (
            operator_metrics["avg_cycle_time"]
            / operator_metrics["avg_actual_duration"]
            * 100
        ).round(2)
        return operator_metrics.reset_index()

    def export_to_csv(self, output_dir: str = "./analytics_output"):
        """Fetch data from MongoDB, compute all analytics, and write CSV + JSON files."""
        os.makedirs(output_dir, exist_ok=True)

        # 1) Fetch raw data
        orders = list(self.orders_collection.find())
        machines = list(self.machines_collection.find())

        # 2) Phase‐level
        print("Extracting phase metrics...")
        phase_df = self.extract_phase_metrics(orders)
        phase_df.to_csv(f"{output_dir}/phase_metrics.csv", index=False)

        # 3) Machine‐level
        print("Calculating machine metrics...")
        machine_metrics = self.calculate_machine_metrics(phase_df, machines)
        machine_metrics.to_csv(f"{output_dir}/machine_metrics.csv", index=False)

        # 4) Order timeline
        print("Generating order timeline...")
        order_timeline = self.generate_order_timeline(orders)
        order_timeline.to_csv(f"{output_dir}/order_timeline.csv", index=False)

        # 5) Queue/bottleneck analysis
        print("Analyzing queue patterns...")
        queue_analysis = self.generate_queue_analysis(phase_df)
        queue_analysis.to_csv(f"{output_dir}/queue_analysis.csv", index=False)

        # 6) Operator performance
        print("Calculating operator performance...")
        operator_performance = self.generate_operator_performance(phase_df)
        operator_performance.to_csv(
            f"{output_dir}/operator_performance.csv", index=False
        )

        # 7) Summary JSON
        summary = {
            "total_orders": len(orders),
            "completed_orders": len(
                [
                    o
                    for o in orders
                    if self._parse_number_int(o.get("orderStatus", None)) == 4
                ]
            ),
            "active_machines": len(
                [m for m in machines if m.get("macchinarioActive", False)]
            ),
            "total_machines": len(machines),
            "avg_order_lead_time": order_timeline["lead_time_days"].mean()
            if "lead_time_days" in order_timeline
            else None,
            "on_time_delivery_rate": (
                order_timeline["on_time"].sum()
                / len(order_timeline[order_timeline["on_time"].notna()])
                * 100
                if "on_time" in order_timeline
                and len(order_timeline[order_timeline["on_time"].notna()]) > 0
                else 0
            ),
            "avg_machine_utilization": machine_metrics["utilization_percentage"].mean()
            if "utilization_percentage" in machine_metrics
            else None,
            "avg_machine_efficiency": machine_metrics["efficiency_percentage"].mean()
            if "efficiency_percentage" in machine_metrics
            else None,
            "total_operators": len(operator_performance)
            if not operator_performance.empty
            else 0,
            "bottleneck_machines": (
                queue_analysis.loc[queue_analysis["is_bottleneck"], "phase_name"].tolist()
                if "phase_name" in queue_analysis.columns
                and "is_bottleneck" in queue_analysis.columns
                else []
            ),
        }

        with open(f"{output_dir}/summary_statistics.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)

        print(f"\nAnalytics exported to `{output_dir}/`")
        print("\nGenerated files:")
        print("- phase_metrics.csv: Detailed phase‐level data")
        print("- machine_metrics.csv: Machine utilization & efficiency")
        print("- order_timeline.csv: Order progress & delays")
        print("- queue_analysis.csv: Queue patterns & bottlenecks")
        print("- operator_performance.csv: Operator efficiency metrics")
        print("- summary_statistics.json: Overall KPIs")

        return summary


if __name__ == "__main__":
    MONGO_URI = (
        "mongodb+srv://demoConsole:GVUoRZio8AEsu2ex@operativoservelessinsta.go3wso0.mongodb.net/?retryWrites=true&w=majority&appName=OperativoServelessInstance"
    )
    ORDERS_DB = "orders_db"
    PROCESS_DB = "process_db"

    analytics = ManufacturingAnalytics(MONGO_URI, ORDERS_DB, PROCESS_DB)
    summary = analytics.export_to_csv()

    print("\nSummary Statistics:")
    for key, value in summary.items():
        print(f"{key}: {value}")
