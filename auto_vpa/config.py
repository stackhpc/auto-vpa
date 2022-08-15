import enum

from pydantic import Field, constr

from configomatic import Configuration as BaseConfiguration, LoggingConfiguration


class Behaviour(str, enum.Enum):
    """
    Enumeration of the possible behaviours.
    """
    CREATE = "Create"
    IGNORE = "Ignore"


class UpdateMode(str, enum.Enum):
    """
    Enumeration of the possible update modes.
    """
    OFF = "Off"
    INITIAL = "Initial"
    RECREATE = "Recreate"
    AUTO = "Auto"


class Configuration(BaseConfiguration):
    """
    Top-level configuration model.
    """
    class Config:
        default_path = "/etc/auto-vpa/config.yaml"
        path_env_var = "AUTO_VPA_CONFIG"
        env_prefix = "AUTO_VPA"

    #: The logging configuration
    logging: LoggingConfiguration = Field(default_factory = LoggingConfiguration)

    #: The annotation to use to define the desired behaviour for a workload
    behaviour_annotation: constr(min_length = 1) = "auto-vpa.stackhpc.com/behaviour"
    #: The default behaviour when the annotation is not present
    default_behaviour: Behaviour = Behaviour.CREATE

    #: The annotation to use to define the update mode
    update_mode_annotation: constr(min_length = 1) = "auto-vpa.stackhpc.com/update-mode"
    #: The default update mode when the annotation is not present
    default_update_mode: UpdateMode = UpdateMode.AUTO


settings = Configuration()
