import pathlib
import typing

import yaml

from .utils import losses, metrics


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
        # Add default parameters
        self.update(
            {
                "optimizer": "Adam",
                "loss": "binary_crossentropy",
                "metrics": ["binary_accuracy"],
                "input_shape": (512, 512, 3),
            }
        )
        self.update(read_config(config_file))

    @property
    def optimizer(self):
        return self["optimizer"]

    @property
    def loss(self):
        loss = self["loss"]
        return getattr(losses, loss, loss)

    @property
    def metrics(self) -> typing.List:
        raw_metrics = self.get_property("metrics", list)
        return [getattr(metrics, m, m) for m in raw_metrics]

    @property
    def input_shape(self) -> typing.Tuple:
        return self.get_property("input_shape", tuple)

    @property
    def output_shape(self) -> typing.Tuple:
        return self.get_property("output_shape", tuple)

    @property
    def base_folder(self) -> pathlib.Path:
        return self.get_property("base_folder", pathlib.Path)

    @property
    def image_folder(self) -> pathlib.Path:
        return self.get_property("image_folder", pathlib.Path)

    @property
    def mask_folder(self) -> pathlib.Path:
        return self.get_property("mask_folder", pathlib.Path)

    @property
    def image_type(self) -> str:
        return self.get_property("image_type", str)

    @property
    def mask_type(self) -> str:
        return self.get_property("mask_type", str)

    @property
    def batch_size(self) -> int:
        return self.get_property("batch_size", int)

    @property
    def epochs(self) -> int:
        return self.get_property("epochs", int)

    @property
    def training_steps(self) -> int:
        return self.get_property("training_steps", int)

    @property
    def validation_steps(self) -> int:
        return self.get_property("validation_steps", int)

    @property
    def seed(self) -> int:
        return self.get_property("seed", int)

    def get_property(self, name: str, cast_to: typing.Any = None):
        prop = self[name]
        if cast_to and not isinstance(prop, cast_to):
            return cast_to(prop)
        return prop

    def get_properties(self) -> typing.Dict:
        return {
            **self,
            **{
                _a: getattr(self, _a)
                for _a in dir(self)
                if isinstance(getattr(type(self), _a), property)
            },
        }
