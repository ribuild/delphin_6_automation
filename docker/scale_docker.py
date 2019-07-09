import subprocess

n = 140 
i = 90
while i < n:
    process = subprocess.Popen(['docker', 'service', 'scale', f'wp6_simulation_ocni={i}'])
    process.wait()
    i += 10

print('Done')
