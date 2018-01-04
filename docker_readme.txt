sudo docker build -t vcd-python-app .
sudo docker run --rm -v ~/vCD:/root -i -t vcd-python-app