# OCI Object Storage Prefix Analyzer
## Purpose
Understand the file counts and byte counts for each prefix in an object storage bucket in OCI.
## Prerequisites
* OCI config file and private key defined in ~/.oci/config
* Python >= 3.9
## Use
```bash
git clone https://github.com/tonymarkel/oci-os-prefix-totals
cd oci-os-prefix-totals
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```
Then open http://localhost:5000

> [!WARNING]
> This is demonstration code meant to help illustrate how to display 
> information from OCI that is not readily available in the console. 
> This code lacks the ability to authenticate and authorize users. 
> It is not fit to deploy in a production environment. If you want a
> command-line verision, use the included os-prefix-totals-to-csv.py

## Command Line Utility

There is an included command line utility to dump the information to csv:
```bash
python os-prefix-totals-to-csv.py --region "<region>" --namespace "<object storage namespace>" --bucket "<bucket name>"
e.g.:
python os-prefix-totals-to-csv.py --region "us-ashburn-1" --namespace "idh3ifrjyvlb" --bucket "TrainingData"
```
