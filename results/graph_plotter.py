import matplotlib.pyplot as plt
import numpy as np
import re
import os

def parse_metrics(file_paths):
    all_metrics = {}
    pattern = re.compile(r'(Accuracy|F1 Score|Precision|Recall|Standard Deviation of Accuracy|Standard Deviation of F1 Score|Standard Deviation of Precision|Standard Deviation of Recall):\s*\[(\d+\.\d+)\]')
    
    for file_path in file_paths:
        metrics = {}
        with open(file_path, 'r') as file:
            for line in file:
                match = pattern.search(line)
                if match:
                    metric = match.group(1).strip()
                    value = float(match.group(2))
                    metrics[metric] = value * 100
        # Extract file name to use as a key for better identification
        file_name = os.path.basename(file_path).replace('.txt', '')
        all_metrics[file_name] = metrics
    return all_metrics

def get_short_name(full_name):
    # Extract the base name without any prefix or suffix
    parts = full_name.split('_')
    return parts[1] if len(parts) > 1 else full_name

# Base directory for files
base_dir = '/home/accmpeg/accmpeg_imp/results'
contents = os.listdir(base_dir)

# Filter file names with '_h265.txt' and '_h264.txt' suffixes
filtered_files = [file.rsplit('_', 1)[0] for file in contents 
                  if file.endswith('_h265.txt') or file.endswith('_h264.txt')]

# Remove duplicate entries
filtered_files = list(set(filtered_files))

# Separate files into categories
category_264 = []
category_265 = []
ext_list = ['_h264.txt', '_h265.txt']
for file in filtered_files:
    for ext in ext_list:
        full_path = os.path.join(base_dir, file + ext)
        if ext == '_h264.txt':
            category_264.append(full_path)
        else:
            category_265.append(full_path)

# Load data from text files
file_paths = {
    'H.264': category_264,
    'H.265': category_265
}
metrics_data = {category: parse_metrics(paths) for category, paths in file_paths.items()}

# Define metrics to plot
metrics = ['Accuracy', 'F1 Score', 'Precision', 'Recall']

# Define patterns for bars
patterns = ['/', '\\', '|', '-']  # Add or modify patterns as needed

# Create separate plots for each metric
for metric in metrics:
    fig, ax = plt.subplots(figsize=(8, 6))
    categories = list(metrics_data.keys())
    num_files = {category: len(metrics_data[category]) for category in categories}
    
    # Compute maximum number of files to set the x-axis range
    max_files = max(num_files.values())
    x = np.arange(max_files)  # the label locations

    width = 0.50  # the width of the bars
    bar_width = width / len(categories)  # Width of each group of bars

    # Plot bars for each category
    for i, (category, data) in enumerate(metrics_data.items()):
        file_names = list(data.keys())
        values = [data.get(file_name, {}).get(metric, 0) for file_name in file_names]
        
        # Compute bar positions
        x_positions = x + (i - len(categories) / 2) * bar_width
        
        # Use hatch patterns for bars
        bars = ax.bar(x_positions, values, bar_width, label=f'{category}', hatch=patterns[i % len(patterns)])

        # Add value labels on the bars
        def add_value_labels(bars):
            for bar in bars:
                height = bar.get_height()
                ax.annotate(f'{height:.1f}',
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom')
        
        add_value_labels(bars)

    # Add some text for labels, title, and custom x-axis tick labels, etc.
    ax.set_xlabel('File')
    ax.set_ylabel('Values')
    ax.set_title(f'Comparison of {metric} for Different Files')
    ax.set_xticks(x)
    
    # Set the x-axis tick labels to the shortened file names
    all_file_names = list(data.keys())
    short_file_names = [get_short_name(name) for name in all_file_names]
    ax.set_xticklabels(short_file_names[:max_files])  # Truncate if more file names than x-axis ticks

    ax.legend()

    fig.tight_layout()
    plt.show()

