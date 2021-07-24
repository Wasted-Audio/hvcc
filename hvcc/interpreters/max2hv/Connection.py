# Copyright 2015 Enzien Audio, Ltd. All Rights Reserved.

class Connection:
    def __init__(self, from_obj_id, outlet_index, to_obj_id, inlet_index, conn_type):
        self.__hv_json = {
            "from": {
                "id": from_obj_id,
                "outlet": outlet_index
            },
            "to": {
                "id": to_obj_id,
                "inlet": inlet_index
            },
            "type": conn_type
        }

    def to_hv(self):
        return self.__hv_json
