function createComponentService(apiService, modalService) {
    var srv = this;

    srv.sendMessage = function (componentUid, message) {
        apiService.executePost(
            "/api/v1/components/" + componentUid + "/process_message",
            message,
            function (response) {
                if (response["type"] !== "success") {
                    delete response["component"];
                    modalService.show("Processing component message failed!", JSON.stringify(response));

                    return;
                }

                if (response["message"] !== undefined) {
                    modalService.show("Command executed", response["message"]);
                }

                if (srv.componentUpdatedCallback !== undefined) {
                    srv.componentUpdatedCallback(response["component"]);
                }
            });
    };

    srv.enable = function (componentUid) {
        apiService.executePost(
            "/api/v1/components/" + componentUid + "/enable",
            null,
            function (response) {
            });
    };

    srv.disable = function (componentUid) {
        apiService.executePost(
            "/api/v1/components/" + componentUid + "/disable",
            null,
            function (response) {
            });
    };

    srv.initialize = function (componentUid) {
        apiService.executePost(
            "/api/v1/components/" + componentUid + "/initialize",
            null,
            function (response) {
            });
    };

    srv.setPositionIndex = function (componentUid, componentGroupUid, value) {
        apiService.executePost(
            "/api/v1/component_groups/" + componentGroupUid + "/components/" + componentUid + "/settings/app.position_index",
            value,
            function (response) {
            });
    };

    return this;
}