# src/presentation/cli/commands.py
import click
import asyncio
from datetime import datetime
from dependency_injector.wiring import inject, Provide
from ...infrastructure.config import Container, Settings
from ...application.dto import GenerateAnalyticsRequest, GetAnalyticsStatusRequest

@click.group()
@click.pass_context
def cli(ctx):
    """Manufacturing Analytics CLI"""
    # Initialize container
    container = Container()
    settings = Settings()
    container.config.from_dict({'settings': settings})
    
    # Wire the container
    container.wire(modules=[__name__])
    
    ctx.obj = container

@cli.command()
@click.option('--output-dir', '-o', help='Output directory for analytics files')
@click.option('--force', '-f', is_flag=True, help='Force regenerate analytics')
@click.pass_context
@inject
async def generate(
    ctx,
    output_dir: str,
    force: bool,
    use_case = Provide[Container.generate_analytics_use_case],
    settings = Provide[Container.settings]
):
    """Generate manufacturing analytics"""
    click.echo("🏭 Generating manufacturing analytics...")
    
    request = GenerateAnalyticsRequest(
        output_directory=output_dir or settings.output_directory,
        force_regenerate=force
    )
    
    result = await use_case.execute(request)
    
    if result.status == 'success':
        click.echo(f"✅ {result.message}")
        click.echo(f"📊 Files generated: {result.files_generated}")
        click.echo("\nSummary:")
        for key, value in result.summary.items():
            click.echo(f"  • {key}: {value}")
    else:
        click.echo(f"❌ {result.message}", err=True)

@cli.command()
@click.option('--include-history', '-h', is_flag=True, help='Include historical data')
@click.option('--limit', '-l', default=10, help='Number of historical records')
@click.pass_context
@inject
async def status(
    ctx,
    include_history: bool,
    limit: int,
    use_case = Provide[Container.get_analytics_status_use_case]
):
    """Check analytics status"""
    click.echo("📊 Checking analytics status...")
    
    request = GetAnalyticsStatusRequest(
        include_history=include_history,
        limit=limit
    )
    
    result = await use_case.execute(request)
    
    if result.status == 'success':
        click.echo(f"\n✅ Status: {result.message}")
        click.echo(f"🕐 Last run: {result.last_run or 'Never'}")
        click.echo(f"⏱️  Next scheduled: {result.next_scheduled_run or 'Not scheduled'}")
        click.echo(f"🚀 Running: {'Yes' if result.is_running else 'No'}")
        click.echo(f"📁 Files available: {len(result.files_available)}")
        
        if result.history:
            click.echo("\n📜 History:")
            for record in result.history:
                click.echo(f"  • {record['timestamp']}: {record['files_generated']} files")
    else:
        click.echo(f"❌ {result.message}", err=True)

@cli.command()
@click.option('--format', '-f', type=click.Choice(['csv', 'json', 'zip']), default='zip')
@click.pass_context
@inject
async def export(
    ctx,
    format: str,
    use_case = Provide[Container.export_analytics_use_case]
):
    """Export analytics data"""
    click.echo(f"📤 Exporting analytics as {format}...")
    
    from ...application.dto import ExportAnalyticsRequest
    
    request = ExportAnalyticsRequest(
        format=format,
        include_summary=True
    )
    
    result = await use_case.execute(request)
    
    if result.status == 'success':
        click.echo(f"✅ {result.message}")
        click.echo(f"📁 File: {result.file_path}")
        click.echo(f"📏 Size: {result.file_size / 1024 / 1024:.2f} MB")
    else:
        click.echo(f"❌ {result.message}", err=True)

@cli.command()
@click.pass_context
@inject
def scheduler(
    ctx,
    scheduler_service = Provide[Container.scheduler_service],
    settings = Provide[Container.settings]
):
    """Start the scheduler service"""
    click.echo("🔄 Starting scheduler service...")
    click.echo(f"⏰ Interval: {settings.schedule_interval_minutes} minutes")
    
    try:
        scheduler_service.start()
        click.echo("✅ Scheduler started. Press Ctrl+C to stop.")
        
        # Keep the scheduler running
        while True:
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n🛑 Stopping scheduler...")
        scheduler_service.stop()
        click.echo("✅ Scheduler stopped.")

def main():
    """CLI entry point"""
    cli(obj={})

if __name__ == '__main__':
    # Handle async commands
    def run_async_command():
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    
    run_async_command()