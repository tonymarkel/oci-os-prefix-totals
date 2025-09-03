# OCI Object Storage Prefix Analyzer
## Purpose
Understand the file counts and byte counts for each prefix in an object storage bucket in OCI.
## Prerequisites
* OCI config file and private key defined in ~/.oci/config
* Python >= 3.9
## Use
```bash
git clone https://github.com/tonymarkel/oci-os-prefix-analyzer
cd oci-os-prefix-analyzer
python -m venv app
source app/bin/activate
python app.py
```
Then open http://localhost:5000

> [!WARNING]
> This is demonstration code meant to help illustrate how to display 
> information from OCI that is not readily available in the console. 
> This code lacks the ability to authenticate and authorize users. 
> It is not fit to deploy in a production environment.