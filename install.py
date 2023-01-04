import launch

if not launch.is_installed('watchdog'):
    launch.run_pip('install watchdog==2.2.1', "requirements for gimp-inpaint")
