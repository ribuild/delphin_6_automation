import subprocess
import time

ret = subprocess.Popen(['docker', 'service', 'inspect', 'wp6_simulation_ocni', "-f '{{ .Spec.Mode.Replicated.Replicas }}'"], stdout=subprocess.PIPE)
i = int(ret.stdout.readline().decode("utf-8").strip(" \n'"))
print(f'\nCurrently there is {i} containers running')


if __name__ == "__main__":
    n = int(input('Docker Containers: '))
    while i < n:
        i += 10
        process = subprocess.Popen(['docker', 'service', 'scale', f'wp6_simulation_ocni={i}'])
        process.wait()
        time.sleep(10)
    print('Done')
