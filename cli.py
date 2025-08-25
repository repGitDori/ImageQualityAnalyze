"""
Command-line interface for ImageQualityAnalyzer
"""

import click
import os
import json
from pathlib import Path
import sys

# Add the package to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from image_quality_analyzer import ImageQualityAnalyzer, load_default_config, load_profile, load_config_from_file
from image_quality_analyzer.config import list_profiles, save_config_to_file
from image_quality_analyzer.visualization import GraphGenerator


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """ImageQualityAnalyzer - Advanced document image quality analysis"""
    pass


@cli.command()
@click.argument('image_path', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Custom configuration file (JSON)')
@click.option('--profile', '-p', type=str, help='Configuration profile name')
@click.option('--output', '-o', type=click.Path(), default='output',
              help='Output directory for reports and graphs')
@click.option('--graphs/--no-graphs', default=True,
              help='Generate visualization graphs')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(image_path, config, profile, output, graphs, verbose):
    """Analyze a single image for quality metrics"""
    
    try:
        # Load configuration
        if config:
            analyzer_config = load_config_from_file(config)
            if verbose:
                click.echo(f"Loaded configuration from: {config}")
        elif profile:
            analyzer_config = load_profile(profile)
            if verbose:
                click.echo(f"Loaded profile: {profile}")
        else:
            analyzer_config = load_default_config()
            if verbose:
                click.echo("Using default configuration")
        
        # Initialize analyzer
        analyzer = ImageQualityAnalyzer(analyzer_config)
        
        # Analyze image
        if verbose:
            click.echo(f"Analyzing image: {image_path}")
        
        result = analyzer.analyze_image(image_path)
        
        # Create output directory
        os.makedirs(output, exist_ok=True)
        
        # Save JSON report
        json_path = os.path.join(output, f"{result['image_id']}_report.json")
        analyzer.export_json_report(result, json_path)
        
        # Print summary
        click.echo(f"\n🔍 Analysis Results for {result['image_id']}")
        click.echo(f"📊 Overall Score: {result['global']['score']:.2f}")
        
        stars = result['global']['stars']
        star_display = '★' * stars + '☆' * (4 - stars)
        click.echo(f"⭐ Star Rating: {star_display} ({stars}/4)")
        
        status = result['global']['status']
        status_emoji = "✅" if status == "pass" else "⚠️" if status == "warn" else "❌"
        click.echo(f"{status_emoji} Status: {status.upper()}")
        
        # Category results
        if verbose:
            click.echo("\n📋 Category Status:")
            for category, cat_status in result['category_status'].items():
                emoji = "✅" if cat_status == "pass" else "⚠️" if cat_status == "warn" else "❌"
                category_name = category.replace('_', ' ').title()
                click.echo(f"  {emoji} {category_name}: {cat_status.upper()}")
        
        # Action items
        actions = result['global']['actions']
        if actions:
            click.echo("\n💡 Recommended Actions:")
            for action in actions:
                click.echo(f"  {action}")
        else:
            click.echo("\n✅ No issues found!")
        
        # Generate graphs
        if graphs:
            if verbose:
                click.echo("\n🎨 Generating visualizations...")
            
            graph_generator = GraphGenerator()
            graph_dir = os.path.join(output, 'graphs')
            os.makedirs(graph_dir, exist_ok=True)
            
            graph_files = graph_generator.generate_all_graphs(image_path, result, graph_dir)
            
            # Create summary dashboard
            dashboard_path = os.path.join(output, f"{result['image_id']}_dashboard.png")
            graph_generator.create_summary_dashboard(result, dashboard_path)
            
            if verbose:
                click.echo(f"Generated {len(graph_files)} visualization files in {graph_dir}")
                click.echo(f"Summary dashboard: {dashboard_path}")
        
        click.echo(f"\n📁 Report saved to: {json_path}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('image_dir', type=click.Path(exists=True, file_okay=False))
@click.option('--config', '-c', type=click.Path(exists=True), 
              help='Custom configuration file (JSON)')
@click.option('--profile', '-p', type=str, help='Configuration profile name')
@click.option('--output', '-o', type=click.Path(), default='batch_output',
              help='Output directory for reports')
@click.option('--csv/--no-csv', default=True, help='Generate CSV comparison')
@click.option('--extensions', default='jpg,jpeg,png,tiff,tif', 
              help='Comma-separated list of file extensions to process')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch(image_dir, config, profile, output, csv, extensions, verbose):
    """Analyze a batch of images in a directory"""
    
    try:
        # Load configuration
        if config:
            analyzer_config = load_config_from_file(config)
        elif profile:
            analyzer_config = load_profile(profile)
        else:
            analyzer_config = load_default_config()
        
        # Initialize analyzer
        analyzer = ImageQualityAnalyzer(analyzer_config)
        
        # Find image files
        ext_list = [f".{ext.strip()}" for ext in extensions.split(',')]
        image_paths = []
        
        for ext in ext_list:
            image_paths.extend(Path(image_dir).glob(f"*{ext}"))
            image_paths.extend(Path(image_dir).glob(f"*{ext.upper()}"))
        
        image_paths = [str(p) for p in image_paths]
        
        if not image_paths:
            click.echo(f"No images found in {image_dir} with extensions: {extensions}")
            sys.exit(1)
        
        click.echo(f"🔍 Found {len(image_paths)} images to analyze")
        
        # Progress callback
        def progress_callback(current, total, path):
            if verbose:
                click.echo(f"Analyzing {current}/{total}: {os.path.basename(path)}")
            else:
                click.echo(f"Progress: {current}/{total}", nl=False)
                click.echo('\r', nl=False)
        
        # Analyze batch
        results = analyzer.analyze_batch(image_paths, progress_callback)
        
        if not verbose:
            click.echo("")  # New line after progress
        
        # Create output directory
        os.makedirs(output, exist_ok=True)
        
        # Statistics
        total_images = len(results)
        valid_results = [r for r in results if 'error' not in r]
        
        click.echo(f"\n📊 Batch Analysis Complete")
        click.echo(f"Total Images: {total_images}")
        click.echo(f"Successfully Analyzed: {len(valid_results)}")
        
        if len(valid_results) < total_images:
            click.echo(f"Errors: {total_images - len(valid_results)}")
        
        # Status distribution
        if valid_results:
            status_counts = {}
            score_sum = 0
            
            for result in valid_results:
                status = result['global']['status']
                status_counts[status] = status_counts.get(status, 0) + 1
                score_sum += result['global']['score']
            
            avg_score = score_sum / len(valid_results)
            click.echo(f"\n📈 Average Score: {avg_score:.2f}")
            
            click.echo("Status Distribution:")
            for status, count in status_counts.items():
                percentage = (count / len(valid_results)) * 100
                emoji = "✅" if status == "pass" else "⚠️" if status == "warn" else "❌"
                click.echo(f"  {emoji} {status.title()}: {count} ({percentage:.1f}%)")
        
        # Export CSV comparison
        if csv:
            csv_path = os.path.join(output, 'batch_comparison.csv')
            analyzer.export_csv_comparison(results, csv_path)
            click.echo(f"\n📋 CSV comparison saved to: {csv_path}")
        
        # Save individual reports
        for result in results:
            if 'error' not in result:
                filename = os.path.join(output, f"{result['image_id']}_report.json")
                analyzer.export_json_report(result, filename)
        
        click.echo(f"📁 Individual reports saved to: {output}")
        
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def profiles():
    """List available configuration profiles"""
    
    profiles_info = list_profiles()
    
    click.echo("Available Configuration Profiles:")
    click.echo("=" * 40)
    
    for profile_id, info in profiles_info.items():
        click.echo(f"\n🔧 {profile_id}")
        click.echo(f"   Name: {info['name']}")
        click.echo(f"   Description: {info['description']}")


@cli.command()
@click.argument('profile_name', type=str)
@click.argument('output_path', type=click.Path())
def export_config(profile_name, output_path):
    """Export a configuration profile to a JSON file"""
    
    try:
        if profile_name == 'default':
            config = load_default_config()
        else:
            config = load_profile(profile_name)
        
        save_config_to_file(config, output_path)
        click.echo(f"✅ Configuration exported to: {output_path}")
        
    except Exception as e:
        click.echo(f"❌ Error exporting configuration: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('config_path', type=click.Path(exists=True))
def validate_config(config_path):
    """Validate a configuration file"""
    
    try:
        from image_quality_analyzer.config import validate_config
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        validate_config(config)
        click.echo(f"✅ Configuration file is valid: {config_path}")
        
    except Exception as e:
        click.echo(f"❌ Configuration validation failed: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
