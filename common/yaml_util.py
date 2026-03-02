import yaml

def read_yaml(file_path):
    """
    YAML工具：读取YAML文件（用于数据驱动、配置读取）
    :param file_path: YAML文件路径
    :return: 字典格式数据
    """
    with open(file_path, "r", encoding="utf-8") as f:
        # 安全加载，防止代码注入
        return yaml.safe_load(f)