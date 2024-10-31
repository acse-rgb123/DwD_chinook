#!/bin/bash

# Navigate to the src/modules directory
cd src/modules || { echo "Modules directory not found"; exit 1; }

# Create __init__.py in the main modules folder
echo "# __init__.py for modules" > __init__.py

# Create __init__.py for each subdirectory
declare -a subdirs=("pipeline" "subgraph")

for dir in "${subdirs[@]}"; do
    mkdir -p "$dir"
    touch "$dir/__init__.py"
    
    # Write initialization code for each subfolder
    case "$dir" in
        "pipeline")
            echo "# __init__.py for pipeline" > pipeline/__init__.py
            echo "from .pipeline import Pipeline" >> pipeline/__init__.py
            echo "from .schema_pipeline import SchemaPipeline" >> pipeline/__init__.py
            echo "from .documentation_pipeline import DocumentationPipeline" >> pipeline/__init__.py
            ;;
        "subgraph")
            echo "# __init__.py for subgraph" > subgraph/__init__.py
            echo "from .schema_extractor import SchemaExtractor" >> subgraph/__init__.py
            echo "from .schema_mapper import SchemaMapper" >> subgraph/__init__.py
            echo "from .subschema import SubschemaCreator" >> subgraph/__init__.py
            ;;
    esac
done

echo "Initialization complete. __init__.py files created and imports set up."
