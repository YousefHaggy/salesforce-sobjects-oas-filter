# Salesforce sObject OAS Filter

A Python command-line tool that filters a Salesforce OpenAPI Specification (OAS) to only include specified sObjects. This tool helps reduce the size of your OAS file by removing unnecessary sObject schemas while preserving common components.

## Features

- Filter OAS specification to keep only specified sObjects
- Preserves non-sObject schemas and common components
- Accept sObject names directly or from a file
- Automatically update SObjectType enum to match filtered schemas
- Maintain JSON structure and formatting of spec

## Requirements

- Python 3.x

## Usage

```bash
python oas_filter.py <input_file> <output_file> --keep <objects>
```

### Parameters

- `input_file`: Path to the input OAS specification JSON file
- `output_file`: Path where the filtered specification will be written
- `--keep`: List of sObject names to preserve (can be direct names or a file path)

### Examples

1. Keep specific sObjects by naming them directly:
```bash
python oas_filter.py input.json output.json --keep Account Contact User
```

2. Keep sObjects listed in a file:
```bash
python oas_filter.py input.json output.json --keep objects.txt
```

Where `objects.txt` contains:
```
Account
Contact
User
```

3. Combine file and direct names:
```bash
python oas_filter.py input.json output.json --keep objects.txt Account Contact
```

## How It Works

1. The tool reads the input OAS specification JSON file
2. It identifies schemas that should be preserved:
   - Specified sObjects from the --keep argument
   - Common components that don't reference SObject
3. Updates the SObjectType enum to remove references to filtered schemas
4. Writes the filtered specification to the output file
