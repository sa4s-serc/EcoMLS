import subprocess

def run_script(script_path, title):
    subprocess.Popen(['gnome-terminal', '--tab', '--title', title, '--', 'bash', '-c', f'python {script_path}; exec bash'])

if __name__ == "__main__":
    process_script_path = "process.py"  # Replace with the path to your process script
    monitor_script_path = "Monitor.py"  # Replace with the path to your Monitor script
    
    run_script(process_script_path, "Process")
    run_script(monitor_script_path, "Monitor")
