# app/utils/bacula_cmd.py
import subprocess
import os
from flask import current_app

def run_bconsole_command(command):
    """Run a command through bconsole and return the output"""
    try:
        # Create a temporary file with the command
        cmd_file = "/tmp/bconsole_cmd.tmp"
        with open(cmd_file, "w") as f:
            f.write(command + "\nquit\n")
        
        # Run bconsole with the command file
        bconsole_path = current_app.config.get('BCONSOLE_PATH', '/usr/sbin/bconsole')
        bconsole_config = current_app.config.get('BCONSOLE_CONFIG', '/etc/bacula/bconsole.conf')
        
        process = subprocess.Popen(
            [bconsole_path, "-c", bconsole_config, "-f", cmd_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = process.communicate()
        
        # Clean up
        os.remove(cmd_file)
        
        if process.returncode != 0:
            return f"Error: {stderr.decode('utf-8')}"
        
        return stdout.decode('utf-8')
    
    except Exception as e:
        return f"Error executing bconsole command: {str(e)}"