# Purpose
使用注册机的机制去注册已经实现的各种功能，完成一个便捷的调用和配置。

# How to use?

1. 实现功能函数或者类，定义好功能入口(main(args))，实现参数接口(parse_args)，例如：
```python 
from gtools.registry import FUNCTION, ARGS

@FUNCTION.regist(module_name='module_name')
def main(args: argparser.Namespace):
    ...

@ARGS.regist(module_name='module_name')
def parse_args():
    parser = argparse.ArgumentParser("test")
    parser.add_argument("--config-file", "-c", type=str, required=True)
    return parser.parse_args()
```

2. 使用的时候可以这样操作，默认配置文件(args中对应的各种参数)配置在`configs/module_name/default.json`中，可以使用`gtools module_name --param1 param1 --param2` 对default中的参数进行覆盖。
```bash
cd gtool_registry_version/
bash ./install.sh
gtools module_name -h 
gtools module_name --param1 param1 --param2
```