import subprocess
import sys
from django.core.management.base import BaseCommand, CommandError
from django.utils.termcolors import make_style

class Command(BaseCommand):
    help = 'Runs the MCP inspector tool against a specified URL.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://127.0.0.1:8000/mcp/sse',
            help='The target MCP SSE URL for the inspector.'
        )

    def handle(self, *args, **options):
        url = options['url']
        command = ['npx', '@modelcontextprotocol/inspector', url]

        success_style = make_style(fg='green', opts=('bold',))
        error_style = make_style(fg='red', opts=('bold',))
        info_style = make_style(fg='cyan')

        self.stdout.write(info_style(f"Attempting to run MCP inspector: {' '.join(command)}"))

        try:
            process = subprocess.run(command, shell=False, check=False, text=True)

            if process.returncode == 0:
                self.stdout.write(success_style(f"MCP Inspector finished successfully (Exit Code: {process.returncode})."))
            else:
                self.stderr.write(error_style(f"MCP Inspector exited with non-zero status (Exit Code: {process.returncode})."))
        except FileNotFoundError:
            self.stderr.write(error_style("Error: 'npx' command not found. Is Node.js and npm/npx installed and in your PATH?"))
            raise CommandError("Required command 'npx' not found.")
        except Exception as e:
            self.stderr.write(error_style(f"An unexpected error occurred: {e}"))
            raise CommandError(f"MCP Inspector execution failed due to an unexpected error: {e}")
