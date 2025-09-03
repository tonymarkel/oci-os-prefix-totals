import oci
import sys
from flask import Flask, render_template, request

# Initialize the Flask application
app = Flask(__name__)

def analyze_bucket_prefixes(region, namespace, bucket_name):
    """
    Analyzes bucket prefixes and returns the data as a list of dictionaries.
    Instead of writing to a file, it returns the results or an error string.
    """
    results = []
    try:
        # Load OCI config from default location (~/.oci/config)
        config = oci.config.from_file()
        object_storage_client = oci.object_storage.ObjectStorageClient(config, region=region)

        # 1. Get all top-level prefixes with pagination
        all_prefixes = []
        next_page = None
        while True:
            list_objects_response = object_storage_client.list_objects(
                namespace_name=namespace,
                bucket_name=bucket_name,
                start=next_page,
                fields="size",
                delimiter='/'
            )
            all_prefixes.extend(list_objects_response.data.prefixes)
            if not list_objects_response.data.next_start_with:
                break
            next_page = list_objects_response.data.next_start_with

        if not all_prefixes:
            return [], "No top-level prefixes found in the specified bucket."

        # 2. Iterate through each prefix and gather stats
        for prefix in all_prefixes:
            file_count = 0
            total_size_bytes = 0
            next_page_objects = None
            while True:
                response = object_storage_client.list_objects(
                    namespace_name=namespace,
                    bucket_name=bucket_name,
                    prefix=prefix,
                    start=next_page_objects,
                    fields="size"
                )
                for obj in response.data.objects:
                    file_count += 1
                    total_size_bytes += obj.size
                if not response.data.next_start_with:
                    break
                next_page_objects = response.data.next_start_with
            
            results.append({
                "prefix": prefix.rstrip('/'),
                "file_count": file_count,
                "total_size_bytes": total_size_bytes
            })
        
        return results, None # Return results and no error

    except oci.exceptions.ServiceError as e:
        error_message = f"OCI Service Error: {e.status} - {e.message}. Please check your credentials and that the bucket details are correct."
        return [], error_message
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        return [], error_message

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        region = request.form.get('region')
        namespace = request.form.get('namespace')
        bucket_name = request.form.get('bucket')

        # Run the analysis
        results, error = analyze_bucket_prefixes(region, namespace, bucket_name)
        
        # Render the results page
        return render_template(
            'results.html', 
            results=results, 
            error=error,
            bucket_name=bucket_name,
            region=region,
            namespace=namespace
        )
    
    # For a GET request, just show the form
    return render_template('index.html')

if __name__ == '__main__':
    # Running in debug mode is convenient for development
    app.run(debug=True, host='0.0.0.0', port=5000)
