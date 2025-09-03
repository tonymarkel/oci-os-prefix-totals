import oci
import sys
import csv
import argparse
from datetime import datetime

def analyze_bucket_prefixes(object_storage_client, namespace, bucket_name):
    """
    Analyzes the prefixes in a bucket and writes the results to a CSV file 
    named after the bucket. Columns are: 
        BUCKET, PREFIX, NUMBER_OF_FILES, TOTAL_SIZE_IN_BYTES
    """
    datetime_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"{bucket_name}_report_{datetime_stamp}.csv"
    print(f"--> Starting analysis. Report will be saved to '{output_filename}'", file=sys.stdout)

    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
            csv_writer = csv.writer(output_file)
            csv_writer.writerow(['BUCKET', 'PREFIX', 'NUMBER_OF_FILES', 'TOTAL_SIZE_IN_BYTES'])

            # Get all top-level prefixes
            print(f"--> Finding prefixes in bucket '{bucket_name}'...", file=sys.stdout)
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
                
                if list_objects_response.data.next_start_with:
                    next_page = list_objects_response.data.next_start_with
                else:
                    break
            
            if not all_prefixes:
                print(f"--> No prefixes found in bucket '{bucket_name}'.", file=sys.stderr)
                return

            print(f"--> Found {len(all_prefixes)} prefixes. Analyzing each...", file=sys.stdout)

            # Iterate through each prefix and gather stats
            for prefix in all_prefixes:
                file_count = 0
                total_size_bytes = 0
                next_page_objects = None
                
                print(f"    -> Processing prefix: {prefix}", file=sys.stdout)

                # Paginate through all objects within the current prefix
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

                    if response.data.next_start_with:
                        next_page_objects = response.data.next_start_with
                    else:
                        break

                csv_writer.writerow([bucket_name, prefix.rstrip('/'), file_count, total_size_bytes])

    # Generic Error Handling
    except oci.exceptions.ServiceError as e:
        print(f"\nError: {e.status} - {e.message}", file=sys.stderr)
        print("Please check if the bucket name, namespace, and region are correct "
              "and that you have the necessary permissions.", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"\nError: Could not write to file '{output_filename}'.", file=sys.stderr)
        print(f"Reason: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"--> Analysis complete. Report saved to '{output_filename}'", file=sys.stdout)


if __name__ == "__main__":

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Analyze an OCI Object Storage bucket and report on the size and file count of its top-level prefixes.")
    parser.add_argument('--region', required=True, help='The OCI region of the bucket (e.g., us-ashburn-1).')
    parser.add_argument('--namespace', required=True, help='The OCI Object Storage namespace.')
    parser.add_argument('--bucket', required=True, help='The name of the bucket to analyze.')
    args = parser.parse_args()

    # Load OCI config and create Object Storage client
    # Note: If you have multiple profiles in your OCI config file, 
    # you can specify the profile name as an argument to from_file()

    # TODO: Allow specifying a profile, instance principals, workload 
    # principals via command-line argument

    config = oci.config.from_file()
    object_storage_client = oci.object_storage.ObjectStorageClient(config, region=args.region)

    # Call the main analysis function
    analyze_bucket_prefixes(object_storage_client, args.namespace, args.bucket)