import pathlib

import umbi.umb
import umbi.umb.index
import umbi.datatypes
import umbi.version

import umbi.umb
from umbi.binary import SizedType


def explicit_umb_to_explicit_ats(umb: umbi.umb.ExplicitUmb) -> umbi.ats.ExplicitAts:
    umb.validate()
    ats = umbi.ats.ExplicitAts()

    ## index
    # skip format_version, format_revision and file_data
    md = umb.index.model_data
    if md is not None:
        ats.model_info = umbi.ats.ModelInfo(
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
    ats.time = umbi.ats.TimeType(ts.time)
    ats.num_players = ts.num_players
    ats.num_states = ts.num_states
    ats.num_initial_states = ts.num_initial_states
    ats.num_choices = ts.num_choices
    ats.num_choice_actions = ts.num_choice_actions
    ats.num_branches = ts.num_branches
    ats.num_branch_actions = ts.num_branch_actions
    ats.player_to_name = ts.player_to_name

    ## values
    ats.state_is_initial = umb.state_is_initial
    ats.state_to_choice = umb.state_to_choices
    ats.state_to_player = umb.state_to_player

    ats.state_is_markovian = umb.state_is_markovian
    ats.state_to_exit_rate = umb.state_to_exit_rate

    ats.choice_to_branches = umb.choice_to_branches
    ats.branch_to_target = umb.branch_to_target
    ats.branch_to_probability = umb.branch_to_probability

    ats.choice_to_choice_action = umb.choice_to_choice_action
    ats.choice_action_to_name = umb.choice_action_to_string
    ats.branch_to_branch_action = umb.branch_to_branch_action
    ats.branch_action_to_name = umb.branch_action_to_string

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
                ats.annotations[category] = dict[str, umbi.ats.Annotation]()
                ats.annotations[category][name] = ats_annotation

    # load valuations
    if umb.index.valuations is not None:
        assert umb.valuations is not None
        ats.variable_valuations = umbi.ats.EntityClassValuations()
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
            ats.variable_valuations.set_valuations_for(entity_class, entity_valuations)

    # load observations
    if ts.observations_apply_to is not None:
        assert ts.num_observations > 0
        assert umb.entity_to_observation is not None
        ats.observation_annotation = umbi.ats.ObservationAnnotation(num_observations=ts.num_observations)
        entity_class = umbi.ats.EntityClass(ts.observations_apply_to)
        ats.observation_annotation.set_values_for(entity_class, umb.entity_to_observation)

    ats.validate()
    return ats


def explicit_ats_to_explicit_umb(ats: umbi.ats.ExplicitAts) -> umbi.umb.ExplicitUmb:
    ats.validate()
    umb = umbi.umb.ExplicitUmb()

    ## index

    umb.index = umbi.umb.index.UmbIndex(
        # insert our format_version, format_revision, file data
        format_version=umbi.version.__format_version__,
        format_revision=umbi.version.__format_revision__,
        file_data=umbi.umb.index.umbi_file_data(),
        # add model data
        model_data=(
            umbi.umb.index.ModelData(
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
        transition_system=umbi.umb.index.TransitionSystem(
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
            player_to_name=ats.player_to_name,
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
        target_type, vector = umbi.datatypes.promote_scalars(ats.state_to_exit_rate)
        assert isinstance(target_type, umbi.datatypes.NumericType), "exit rates must be numeric"
        umb.index.transition_system.exit_rate_type = SizedType.for_type(target_type)
        umb.state_to_exit_rate = vector  # type: ignore

    umb.choice_to_branches = ats.choice_to_branches
    umb.branch_to_target = ats.branch_to_target

    if ats.branch_to_probability is not None:
        # promote
        target_type, vector = umbi.datatypes.promote_scalars(ats.branch_to_probability)
        assert isinstance(target_type, umbi.datatypes.NumericType), "branch probabilities must be numeric"
        umb.index.transition_system.branch_probability_type = SizedType.for_type(target_type)
        umb.branch_to_probability = vector  # type: ignore

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
        umb.index.annotations[category] = dict[str, umbi.umb.index.AnnotationDescription]()
        umb.annotations[category] = dict[str, dict[str, list]]()
        for name, ats_annotation in name_to_annotation.items():
            # determine common type of values for this annotation
            target_type = ats_annotation.get_common_type()
            umb_annotation = umbi.umb.index.AnnotationDescription(
                alias=ats_annotation.alias,
                description=ats_annotation.description,
                applies_to=[entity_class.value for entity_class in ats_annotation.entity_classes],  # type: ignore
                type=SizedType.for_type(target_type),
                lower=None,  # TODO add later
                upper=None,  # TODO add later
            )
            umb.index.annotations[category][name] = umb_annotation
            umb.annotations[category][name] = dict[str, list]()
            for entity_class in ats_annotation.entity_classes:
                values = ats_annotation._entity_class_to_values[entity_class]
                values = umbi.datatypes.promote_scalars_to(values, target_type)
                umb.annotations[category][name][entity_class.value] = values

    # add valuations
    if ats.variable_valuations is not None:
        umb.index.valuations = {}
        umb.valuations = {}
        for entity_class, entity_valuations in ats.variable_valuations.items():
            applies_to = entity_class.value
            valuation_class = umbi.binary.StructType()

            # promote values for each variable to a common type
            # calculate the required bitsize
            var_values = {}
            for var in entity_valuations.variables:
                values = entity_valuations.get_variable_valuations(var).values
                assert None not in values, "valuation variables cannot have None values"
                target_type, values = umbi.datatypes.promote_scalars(values)  # type: ignore
                var_values[var] = values
                num_bits = umbi.binary.max_num_bits_for_collection_element(values, target_type)
                valuation_class.add_attribute(
                    name=var.name,
                    sized_type=SizedType(type=var.promotion_type, size_bits=num_bits),
                )
            valuation_class.pad_to_byte()
            valuation_description = umbi.umb.index.ValuationDescription(
                unique=False,  # for now
                num_strings=None,  # TODO add later
                classes=[valuation_class],
            )
            valuation_description.unique = entity_valuations.has_distinct_valuations
            umb.index.valuations[applies_to] = valuation_description
            umb.valuations[applies_to] = []
            for entity in range(entity_valuations.num_entities):
                valuations = {var.name: var_values[var][entity] for var in entity_valuations.variables}
                umb.valuations[applies_to].append(valuations)

    # add observations
    if ats.observation_annotation is not None:
        umb.index.transition_system.observations_apply_to = ats.observation_annotation.entity_class.value  # type: ignore
        umb.index.transition_system.num_observations = ats.observation_annotation.num_observations
        umb.entity_to_observation = ats.observation_annotation.values

    umb.validate()
    return umb


# API


def read(umbpath: str | pathlib.Path, strict: bool = False) -> umbi.ats.ExplicitAts:
    """Read ATS from a umbfile.

    :param umbpath: path to the umbfile
    :param strict: in the strict mode, unread files will raise an error
    :return: ExplicitAts object containing the data from the umbfile
    """
    umb = umbi.umb.read(umbpath, strict=strict)
    ats = explicit_umb_to_explicit_ats(umb)
    return ats


def write(ats: umbi.ats.ExplicitAts, umbpath: str | pathlib.Path) -> None:
    """Write ATS to a umbfile.

    :param ats: ExplicitAts object to write
    :param umbpath: path to the umbfile to write to
    """
    umb = explicit_ats_to_explicit_umb(ats)
    umbi.umb.write(umb, umbpath)
