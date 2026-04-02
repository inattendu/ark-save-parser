from typing import Dict, List, Optional, TYPE_CHECKING
import uuid
from pathlib import Path
import random
import json

from arkparse.parsing.struct import ActorTransform
from .header_location import HeaderLocation
# from arkparse.object_model.npc_zone_volume import NpcZoneVolume

class SaveContext:
    def __init__(self):
        self.names: Dict[int, str] = {}
        self._name_reverse: Dict[str, int] = {}  # reverse lookup: name -> id
        self.constant_name_table: Optional[Dict[int, str]] = None
        self.some_other_table: Optional[Dict[int, str]] = None
        self.sections: List[HeaderLocation] = []
        self.actor_transforms: Dict[uuid.UUID, ActorTransform] = {}
        self.actor_transform_positions: Dict[uuid.UUID, int] = {}
        self.save_version: int = 0
        self.game_time: float = 0.0
        self.map_name: str = ""
        self.unknown_value: int = 0
        self.npc_zone_volumes: List["NpcZoneVolume"] = []
        self.all_uuids: List[uuid.UUID] = []
        self.generate_unknown: bool = False
        self.current_time = 0
        self.current_day = 0

    def get_actor_transform(self, uuid_: uuid.UUID) -> Optional[ActorTransform]:
        return self.actor_transforms.get(uuid_)

    def has_name_table(self) -> bool:
        return (self.names is not None and len(self.names) != 0) or self.constant_name_table is not None 

    def get_name(self, key: int) -> Optional[str]:
        if key in self.names:
            return self.names[key]
        elif self.constant_name_table and key in self.constant_name_table:
            return self.constant_name_table[key]
        elif self.generate_unknown:
            unknown_name = f"Unknown_{key}"
            self.names[key] = unknown_name
            return unknown_name
        return None

    def use_constant_name_table(self, constant_name_table: Dict[int, str]):
        self.constant_name_table = constant_name_table

    def is_read_names_as_strings(self) -> bool:
        return self.save_version >= 13
    
    def store_names_to_json(self, path: Path):
        with open(path, "w") as f:
            json.dump(self.names, f, indent=4)

    def get_name_id(self, name: str) -> Optional[int]:
        return self._name_reverse.get(name)

    def _rebuild_reverse_cache(self) -> None:
        """Rebuild the reverse name lookup from self.names."""
        self._name_reverse = {v: k for k, v in self.names.items()}

    def add_new_name(self, name: str, id: int = None) -> int:
        if id is not None:
            self.names[id] = name
            self._name_reverse[name] = id
            return id

        new_id = random.randint(0, int(2**31 - 1))
        while new_id in self.names:
            new_id = random.randint(0, int(2**31 - 1))
        self.names[new_id] = name
        self._name_reverse[name] = new_id

        return new_id