import { Fragment } from "react";
import {
    AutocompleteInput,
    DatagridConfigurable,
    DateField,
    List,
    ReferenceInput,
    SelectColumnsButton,
    TextField,
    TextInput,
    TopToolbar,
} from "react-admin";

import { CustomPagination } from "../../commons/custom_fields/CustomPagination";
import { AutocompleteInputMedium } from "../layout/themes";
import { getSettingListSize } from "../settings/functions";
import { TYPE_CHOICES } from "../types";
import NotificationBulkDeleteButton from "./NotificationBulkDeleteButton";

const listFilters = [
    <AutocompleteInput source="type" choices={TYPE_CHOICES} alwaysOn />,
    <TextInput source="name" alwaysOn />,
    <TextInput source="message" alwaysOn />,
    <TextInput source="function" alwaysOn />,
    <ReferenceInput source="product" reference="products" sort={{ field: "name", order: "ASC" }} alwaysOn>
        <AutocompleteInputMedium optionText="name" />
    </ReferenceInput>,
    <ReferenceInput source="user" reference="users" sort={{ field: "full_name", order: "ASC" }} alwaysOn>
        <AutocompleteInputMedium optionText="full_name" />
    </ReferenceInput>,
];

const BulkActionButtons = () => (
    <Fragment>
        <NotificationBulkDeleteButton />
    </Fragment>
);

const ListActions = () => (
    <TopToolbar>
        <SelectColumnsButton />
    </TopToolbar>
);

const NotificationList = () => {
    return (
        <List
            perPage={25}
            pagination={<CustomPagination />}
            filters={listFilters}
            sort={{ field: "created", order: "DESC" }}
            disableSyncWithLocation={false}
            storeKey="notifications.list"
            actions={<ListActions />}
        >
            <DatagridConfigurable size={getSettingListSize()} rowClick="show" bulkActionButtons={<BulkActionButtons />}>
                <TextField source="type" />
                <TextField source="name" />
                <DateField source="created" showTime={true} />
                <TextField source="message" />
                <TextField source="function" />
                <TextField source="product_name" label="Product" />
                <TextField source="observation_title" label="Observation" />
                <TextField source="user_full_name" label="User" />
            </DatagridConfigurable>
        </List>
    );
};

export default NotificationList;
