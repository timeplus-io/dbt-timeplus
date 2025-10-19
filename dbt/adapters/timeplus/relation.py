from dataclasses import dataclass, field
from typing import Any, Optional, Type

from dbt.adapters.base.relation import BaseRelation, Policy, Self
from dbt.contracts.graph.nodes import SourceDefinition
from dbt_common.dataclass_schema import StrEnum
from dbt.exceptions import DbtRuntimeError
from dbt_common.utils import deep_merge


@dataclass
class ProtonQuotePolicy(Policy):
    database: bool = False
    schema: bool = False
    identifier: bool = False


@dataclass
class ProtonIncludePolicy(Policy):
    database: bool = False
    schema: bool = True
    identifier: bool = True

class ProtonRelationType(StrEnum):
    Table = "table"
    View = "view"
    CTE = "cte"
    MaterializedView = "materialized_view"
    External = "external"
    Ephemeral = "ephemeral"
    Dictionary = "dictionary"


@dataclass(frozen=True, eq=False, repr=False)
class ProtonRelation(BaseRelation):
    quote_policy: Policy = field(default_factory=lambda: ProtonQuotePolicy())
    include_policy: Policy = field(default_factory=lambda: ProtonIncludePolicy())
    quote_character: str = ''
    can_exchange: bool = False

    def render(self):
        if self.include_policy.database and self.include_policy.schema:
            raise DbtRuntimeError(
                'Got a Proton relation with schema and database set to '
                'include, but only one can be set'
            )
        return super().render()

    def matches(
        self,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        identifier: Optional[str] = None,
    ):
        # if schema:
        #     raise DbtRuntimeError(f'Passed unexpected schema value {schema} to Relation.matches')
        return self.database == database and self.identifier == identifier

    @classmethod
    def create_from_source(cls: Type[Self], source: SourceDefinition, **kwargs: Any) -> Self:
        source_quoting = source.quoting.to_dict(omit_none=True)
        source_quoting.pop("column", None)
        quote_policy = deep_merge(
            cls.get_default_quote_policy().to_dict(omit_none=True),
            source_quoting,
            kwargs.get("quote_policy", {}),
        )

        # If the database is set, and the source schema is "defaulted" to the source.name, override the
        # schema with the database instead, since that's presumably what's intended for Proton
        schema = source.schema
        if schema == source.source_name and source.database:
            schema = source.database

        return cls.create(
            database=source.database,
            schema=schema,
            identifier=source.identifier,
            quote_policy=quote_policy,
            **kwargs,
        )
