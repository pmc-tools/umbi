import pathlib
import time

import umbi

from .umb import ExplicitUmb, read_umb, write_umb


def umbi_file_data() -> umbi.index.FileData:
    """Generate UMB file data for use in umb files created by umbi."""
    return umbi.index.FileData(
        tool=umbi.version.__toolname__,
        tool_version=umbi.version.__version__,
        creation_date=int(time.time()),
        # parameters=parameters,
    )


def explicit_umb_to_explicit_ats(umb: ExplicitUmb) -> umbi.ats.ExplicitAts:
    umb.validate()
    explicit_ats = umbi.ats.ExplicitAts()

    ## index
    # skip format_version, format_revision and file_data
    md = umb.index.model_data
    if md is not None:
        explicit_ats.model_info = umbi.ats.ModelInfo(
            name=md.name,
            version=md.version,
            authors=md.authors,
            description=md.description,
            comment=md.comment,
            doi=md.doi,
            url=md.url,
        )
    # load index.transition_system
    ts = umb.index.transition_system
    explicit_ats.time = umbi.ats.TimeType(ts.time)
    explicit_ats.num_players = ts.num_players
    explicit_ats.num_states = ts.num_states
    explicit_ats.num_initial_states = ts.num_initial_states
    explicit_ats.num_choices = ts.num_choices
    explicit_ats.num_choice_actions = ts.num_choice_actions
    explicit_ats.num_branches = ts.num_branches
    explicit_ats.num_branch_actions = ts.num_branch_actions
    explicit_ats.player_to_name = ts.player_names

    ## values
    explicit_ats.state_is_initial = umb.state_is_initial
    explicit_ats.state_to_choice = umb.state_to_choices
    explicit_ats.state_to_player = umb.state_to_player

    explicit_ats.state_is_markovian = umb.state_is_markovian
    explicit_ats.state_to_exit_rate = umb.state_to_exit_rate

    explicit_ats.choice_to_branches = umb.choice_to_branches
    explicit_ats.branch_to_target = umb.branch_to_target
    explicit_ats.branch_to_probability = umb.branch_to_probability

    explicit_ats.choice_to_choice_action = umb.choice_to_choice_action
    explicit_ats.choice_action_to_name = umb.choice_action_to_string
    explicit_ats.branch_to_branch_action = umb.branch_to_branch_action
    explicit_ats.branch_action_to_name = umb.branch_action_to_string

    # load annotations
    if umb.index.annotations is not None:
        assert umb.annotations is not None
        for category, name_to_annotation in umb.index.annotations.items():
            constructor = {
                "rewards": umbi.ats.RewardAnnotation,
                "aps": umbi.ats.AtomicPropositionAnnotation,
            }[category] or umbi.ats.Annotation
            for name, umb_annotation in name_to_annotation.items():
                ats_annotation = constructor(
                    name=name,
                    alias=umb_annotation.alias,
                    description=umb_annotation.description,
                )
                for applies_to in umb_annotation.applies_to or []:
                    values = umb.annotations[category][name][applies_to]
                    entity_class = umbi.ats.EntityClass(applies_to)
                    ats_annotation.set_values_for(entity_class, values)
                explicit_ats.annotations[category] = dict[str, umbi.ats.Annotation]()
                explicit_ats.annotations[category][name] = ats_annotation

    # load valuations
    if umb.index.valuations is not None:
        assert umb.valuations is not None
        explicit_ats.variable_valuations = umbi.ats.EntityClassValuations()
        for applies_to, valuation_description in umb.index.valuations.items():
            # ignore unique and num_strings
            # assume a single valuation class
            if len(valuation_description.classes) > 1:
                raise NotImplementedError("multiple valuation classes not supported yet")
            struct_type = valuation_description.classes[0]

            entity_to_valuation = umb.valuations[applies_to]
            entity_class = umbi.ats.EntityClass(applies_to)
            entity_valuations = umbi.ats.EntityValuations()
            for attribute in struct_type.attributes:
                if attribute.lower is not None or attribute.upper is not None:
                    raise NotImplementedError("bounds on valuation variables not supported yet")
                if attribute.offset is not None and attribute.offset != 0:
                    raise NotImplementedError("offsets on valuation variables not supported yet")
                entity_valuations.add_variable(variable_name=attribute.name)
            for entity, valuation in enumerate(entity_to_valuation):
                valuation = {entity_valuations.get_variable(var_name): value for var_name, value in valuation.items()}
                entity_valuations.set_entity_valuation(entity, valuation)
            explicit_ats.variable_valuations.set_valuations_for(entity_class, entity_valuations)

    # load observations
    if ts.observations_apply_to is not None:
        assert ts.num_observations > 0
        assert umb.entity_to_observation is not None
        explicit_ats.observation_annotation = umbi.ats.ObservationAnnotation(num_observations=ts.num_observations)
        entity_class = umbi.ats.EntityClass(ts.observations_apply_to)
        explicit_ats.observation_annotation.set_values_for(entity_class, umb.entity_to_observation)

    explicit_ats.validate()
    return explicit_ats


def explicit_ats_to_explicit_umb(ats: umbi.ats.ExplicitAts) -> ExplicitUmb:
    ats.validate()
    umb = ExplicitUmb()

    ## index

    umb.index = umbi.index.UmbIndex(
        # insert our format_version, format_revision, file data
        format_version=umbi.version.__format_version__,
        format_revision=umbi.version.__format_revision__,
        file_data=umbi_file_data(),
        # add model data
        model_data=(
            umbi.index.ModelData(
                name=ats.model_info.name,
                version=ats.model_info.version,
                authors=ats.model_info.authors,
                description=ats.model_info.description,
                comment=ats.model_info.comment,
                doi=ats.model_info.doi,
                url=ats.model_info.url,
            )
            if ats.model_info is not None
            else None
        ),
        transition_system=umbi.index.TransitionSystem(
            time=ats.time.value,
            num_players=ats.num_players,
            num_states=ats.num_states,
            num_initial_states=ats.num_initial_states,
            num_choices=ats.num_choices,
            num_choice_actions=ats.num_choice_actions,
            num_branches=ats.num_branches,
            num_branch_actions=ats.num_branch_actions,
            num_observations=ats.num_observations,
            observations_apply_to=None,  # for now
            branch_probability_type=None,  # for now
            exit_rate_type=None,  # for now
            observation_probability_type=None,  # for now
            player_names=ats.player_to_name,
        ),
        # create annotations
        annotations=None,  # for now
        valuations=None,  # for now
    )

    ## values
    # warning: this does not copy the values, but directly uses the lists from ats.
    # this is fine as long as we don't modify them
    umb.state_is_initial = ats.state_is_initial
    umb.state_to_choices = ats.state_to_choice
    umb.state_to_player = ats.state_to_player

    umb.state_is_markovian = ats.state_is_markovian
    if ats.state_to_exit_rate is not None:
        # promote all to common type
        target_type = umbi.datatypes.common_collection_element_type(ats.state_to_exit_rate)
        assert isinstance(target_type, umbi.datatypes.NumericType), "exit rates must be numeric"
        # do we need to promote ints?
        # if target_type == umbi.datatypes.NumericPrimitiveType.INT:
        #     # implicit promotion of int to double
        #     target_type = umbi.datatypes.NumericPrimitiveType.DOUBLE
        umb.index.transition_system.exit_rate_type = umbi.datatypes.SizedType(type=target_type)
        umb.state_to_exit_rate = umbi.datatypes.promote_vector_to(ats.state_to_exit_rate, target_type)  # type: ignore

    umb.choice_to_branches = ats.choice_to_branches
    umb.branch_to_target = ats.branch_to_target

    if ats.branch_to_probability is not None:
        # promote
        target_type = umbi.datatypes.common_collection_element_type(ats.branch_to_probability)
        assert isinstance(target_type, umbi.datatypes.NumericType), "branch probabilities must be numeric"
        umb.index.transition_system.branch_probability_type = umbi.datatypes.SizedType(type=target_type)
        umb.branch_to_probability = umbi.datatypes.promote_vector_to(ats.branch_to_probability, target_type)  # type: ignore

    umb.choice_to_choice_action = ats.choice_to_choice_action
    umb.choice_action_to_string = ats.choice_action_to_name
    umb.branch_to_branch_action = ats.branch_to_branch_action
    umb.branch_action_to_string = ats.branch_action_to_name

    # add annotations
    umb.index.annotations = {}
    umb.annotations = {}
    for category, name_to_annotation in ats.annotations.items():
        if len(name_to_annotation) == 0:
            continue
        umb.index.annotations[category] = dict[str, umbi.index.Annotation]()
        umb.annotations[category] = dict[str, dict[str, list]]()
        for name, ats_annotation in name_to_annotation.items():
            # determine common type of values for this annotation
            types = {
                umbi.datatypes.common_collection_element_type(values)
                for values in ats_annotation._entity_class_to_values.values()
            }
            target_type = umbi.datatypes.common_datatype(types)
            umb_annotation = umbi.index.Annotation(
                alias=ats_annotation.alias,
                description=ats_annotation.description,
                applies_to=[entity_class.value for entity_class in ats_annotation.entity_classes],  # type: ignore
                type=umbi.datatypes.SizedType(type=target_type),
                lower=None,  # TODO add later
                upper=None,  # TODO add later
            )
            umb.index.annotations[category][name] = umb_annotation
            umb.annotations[category][name] = dict[str, list]()
            for entity_class in ats_annotation.entity_classes:
                values = ats_annotation._entity_class_to_values[entity_class]
                values = umbi.datatypes.promote_vector_to(values, target_type)  # type: ignore
                umb.annotations[category][name][entity_class.value] = values

    # add valuations
    if ats.variable_valuations is not None:
        umb.index.valuations = {}
        umb.valuations = {}
        for entity_class, entity_valuations in ats.variable_valuations.items():
            applies_to = entity_class.value
            valuation_class = umbi.datatypes.StructType()
            for var in entity_valuations.variables:
                valuation_class.add_attribute(
                    name=var.name,
                    sized_type=umbi.datatypes.SizedType(type=var.type),  # TODO deduce non-default size from the values
                )
            valuation_class.pad_to_byte()
            valuation_description = umbi.index.ValuationDescription(
                unique=False,  # TODO add later
                num_strings=None,  # TODO add later
                classes=[valuation_class],
            )
            umb.index.valuations[applies_to] = valuation_description
            umb.valuations[applies_to] = []
            for entity in range(entity_valuations.num_entities):
                valuations = entity_valuations.get_entity_valuation(entity)
                valuations = {var.name: value for var, value in valuations.items()}
                umb.valuations[applies_to].append(valuations)

    # add observations
    if ats.observation_annotation is not None:
        umb.index.transition_system.observations_apply_to = ats.observation_annotation.entity_class.value  # type: ignore
        umb.index.transition_system.num_observations = ats.observation_annotation.num_observations
        umb.entity_to_observation = ats.observation_annotation.values

    umb.validate()
    return umb


def read_ats(umbpath: str | pathlib.Path) -> umbi.ats.ExplicitAts:
    """Read ATS from a umbfile."""
    umb = read_umb(umbpath)
    ats = explicit_umb_to_explicit_ats(umb)
    return ats


def write_ats(ats: umbi.ats.ExplicitAts, umbpath: str | pathlib.Path) -> None:
    """Write ATS to a umbfile."""
    umb = explicit_ats_to_explicit_umb(ats)
    write_umb(umb, umbpath)
