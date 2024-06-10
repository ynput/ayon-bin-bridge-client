def test_direct_write_out():
    import subprocess
    import sys
    import select
    import time

    command = ["bash", "-c", "for i in {1..20}; do echo 'Output message testing'; sleep 0.1; done"]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, universal_newlines=True)

    while process.poll() is None:
        # Check if there's data available to read
        if select.select([process.stdout], [], [], 0.1)[0]:
            # Read and print the output
            sys.stdout.write(process.stdout.readline())
            sys.stdout.flush()

    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()









