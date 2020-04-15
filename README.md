# Picasso

https://challengedata.ens.fr/participants/challenges/25/

### Installing

```
conda create -n picasso_venv
conda install -c conda-forge -n picasso_venv --file requirements.txt
```

### Generate self-signed certificate

```
openssl req -config [LETTER]:\path\to\Anaconda3\Library\openssl.cnf -x509 -newkey rsa:4096 -nodes -out mycert.pem -keyout mycert.pem -days 365
```
