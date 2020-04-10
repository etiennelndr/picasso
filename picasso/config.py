import pathlib
import typing

import yaml


def read_config(config_file: pathlib.Path) -> typing.Dict:
    """
    Reads a config file :param:`config_file` as a :py:class:`dict`.

    :raises:
        - FileNotFoundError: Config file doesn't exist.
        - ValueError: Unsupported config file extension.
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Config file {config_file} doesn't exist.")

    if "yaml" in config_file.suffix:
        return _read_yaml_config(config_file)
    else:
        raise ValueError("Unsupported config file extension.")


def _read_yaml_config(config_file: pathlib.Path) -> typing.Dict:
    with open(str(config_file), "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as err:
            raise yaml.YAMLError(f"Error when reading yaml file: {err}.")


class Config(dict):
    def __init__(self, config_file: pathlib.Path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.update({
            "optimizer": "Adam",
            "loss": "binary_crossentropy",
            "metrics": ["binary_accuracy"],
            "input_shape": (512, 512, 3)
        })
        self.update(read_config(config_file))

    @property
    def optimizer(self):
        return self["optimizer"]

    @property
    def loss(self):
        return self["loss"]

    @property
    def metrics(self) -> typing.List:
        return list(self["metrics"])

    @property
    def input_shape(self) -> typing.Tuple:
        return tuple(self["input_shape"])


