#!/bin/bash

# 检查参数是否正确
if [ "$#" -ne 2 ]; then
  echo "用法: ./split.sh 文件名 N"
  exit 1
fi

# 获取输入文件名和分割份数
input_file=$1
N=$2

# 检查输入文件是否存在
if [ ! -f "$input_file" ]; then
  echo "文件 $input_file 不存在"
  exit 1
fi

# 获取源文件所在的目录和前缀
file_dir=$(dirname "$input_file")
file_prefix=$(basename "${input_file%.*}")
output_dir="${file_dir}/split_${file_prefix}"
mkdir -p "$output_dir"

# 计算每一份的行数
total_lines=$(wc -l < "$input_file")
lines_per_file=$(( (total_lines + N - 1) / N ))  # 向上取整

# 使用 split 命令按行数拆分并重命名
split -l "$lines_per_file" "$input_file" "${output_dir}/${file_prefix}_temp_"

# 将生成的文件重命名为所需格式
count=1
for file in "${output_dir}/${file_prefix}_temp_"*; do
  mv "$file" "${output_dir}/${file_prefix}_${count}.txt"
  ((count++))
done

echo "文件已成功拆分成 ${N} 份，并存放在文件夹 ${output_dir} 中。"