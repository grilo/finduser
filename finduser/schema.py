#!/usr/bin/env python
import logging

class Validator:

    def __init__(self, schema={}):
        self.schema = schema

    def coerce_values(self, struct):
        for k, v in struct.items():
            try:
                struct[k] = self.schema[k](v)
            except ValueError:
                continue
        return struct

    """
        Assert:
            * Keys on the right_side exist on the left_side
            * Values on the right_side match the ones on the left_side
    """
    def _validate(self, right_side, left_side):
        error_count = 0
        for k, v in right_side.items():
            try:
                assert k in right_side.keys()
            except AssertionError:
                error_count += 1
                logging.error("Keys (%s) should exist in %s" % (k, right_side.keys()))

            try:
                if type(v) == type(type) and type(left_side[k]) != type(type):
                    assert v == type(left_side[k])
                elif type(left_side[k]) == type(type):
                    assert type(v) == left_side[k]
                else:
                    assert v == left_side[k]
            except AssertionError:
                error_count += 1
                logging.error("Invalid value type detected: (%s) != (%s)" % (v, left_side[k]))
        if error_count > 0:
            return False
        return True

    def full(self, struct):
        return self._validate(self.schema, struct)

    def partial(self, struct):
        return self._validate(self.coerce_values(struct), self.schema)
