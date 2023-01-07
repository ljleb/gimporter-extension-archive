import launch

if not launch.is_installed('watchdog'):
    desc = 'requirements for gimporter'
    launch.run_pip('install websockets==10.4', desc)
