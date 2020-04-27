# Picasso

https://challengedata.ens.fr/participants/challenges/25/

### Installing

Create a new conda environment and install the packages from `requirements.txt`:
```
conda create -n picasso_venv
conda install -c conda-forge -n picasso_venv --file requirements.txt
```

Install pre-commit hook:
```
pre-commit install
```

### Generate self-signed certificate

```
openssl req -config [LETTER]:\path\to\Anaconda3\Library\openssl.cnf -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
```

### Validate WSS

Inside a webbrower, for a given web socket server `wss://IP_ADDRESS:PORT`, open the following link and accept the
certificate:
```
https://IP_ADDRESS:PORT`
```
