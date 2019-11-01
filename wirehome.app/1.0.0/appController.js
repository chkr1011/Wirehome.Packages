function createAppController($http, $scope, apiService, localizationService, componentService, macroService, notificationService) {
    var c = this;

    extendAngularScope($scope);

    c.version = "-";
    c.notifications = [];
    c.panels = [];
    c.componentGroups = [];
    c.globalVariables = {};

    c.notificationService = notificationService;
    c.componentService = componentService;
    c.macroService = macroService;
    c.localizationService = localizationService;
    c.apiService = apiService;

    c.hasGlobalVariable = function (uid) {
        c.globalVariables.hasOwnProperty(uid);
    };

    c.getGlobalVariable = function (uid, defaultValue) {
        return getValue(c.globalVariables, uid, defaultValue);
    };

    c.setActivePanel = function (uid) {
        if (c.activePanel === uid) {
            c.activePanel = "";
        } else {
            c.activePanel = uid;
        }

        setTimeout(function () {
            $("html, body").animate({
                scrollTop: $("#" + uid).offset().top
            },
                250);
        },
            100);
    };

    c.applyNewComponentStatus = function (updatedComponent) {
        $.each(c.componentGroups,
            function (i, componentGroupModel) {
                $.each(componentGroupModel.components,
                    function (j, componentModel) {
                        if (componentModel.uid === updatedComponent.uid) {
                            c.configureComponent(componentModel, updatedComponent, componentGroupModel);
                        }
                    });

                // $.each(componentGroupModel.macros, function (j, marcoModel) {
                //     if (marcoModel.uid == updatedMacro.uid) {
                //         c.configureMacro(marcoModel, updatedMacro, componentGroupModel)
                //     }
                // });
            });
    };

    c.applyNewStatus = function (status) {
        if (c.isConfigured !== true) {
            console.log("Building UI...");
            localizationService.load(status.global_variables["system.language_code"]);

            $.each(status.componentGroups, function (i, componentGroup) {
                if (componentGroup.settings["app.is_visible"] === false) {
                    return;
                }

                var componentGroupModel = {
                    uid: componentGroup.uid,
                    source: {},
                    settings: {},
                    components: [],
                    macros: [],
                    hasSetting: function (uid) {
                        return componentGroupModel.settings.hasOwnProperty(uid);
                    },
                    getSetting: function (uid, defaultValue) {
                        return getValue(componentGroupModel.settings, uid, defaultValue);
                    }
                };

                $.each(componentGroup.components, function (i) {
                    var componentModel = {
                        uid: i,
                        source: {},
                        status: {},
                        settings: {},
                        configuration: {},
                        showMore: false,
                        toggleShowMore: function () {
                            componentModel.showMore = !componentModel.showMore;
                        },
                        hasStatus: function (uid) {
                            return componentModel.status.hasOwnProperty(uid);
                        },
                        getStatus: function (uid, defaultValue) {
                            return getValue(componentModel.status, uid, defaultValue);
                        },
                        hasSetting: function (uid) {
                            var associationSettings = componentGroupModel.source.components[componentModel.uid].settings;
                            return associationSettings.hasOwnProperty(uid) ||
                                componentModel.settings.hasOwnProperty(uid);
                        },
                        getSetting: function (uid, defaultValue) {
                            var associationSettings = componentGroupModel.source.components[componentModel.uid].settings;
                            return getEffectiveValue([associationSettings, componentModel.settings],
                                uid,
                                defaultValue);
                        },
                        hasConfiguration: function (uid) {
                            return componentModel.source.configuration.hasOwnProperty(uid);
                        },
                        getConfiguration: function (uid, defaultValue) {
                            return getValue(componentModel.source.configuration, uid, defaultValue);
                        }
                    };

                    componentGroupModel.components.push(componentModel);
                });

                $.each(componentGroup.macros, function (i) {
                    var macroModel = {
                        uid: i,
                        source: {},
                        hasSetting: function (uid) {
                            var associationSettings = macroModel.source.macros[macroModel.uid].settings;
                            return associationSettings.hasOwnProperty(uid) ||
                                macroModel.source.settings.hasOwnProperty(uid);
                        },
                        getSetting: function (uid, defaultValue) {
                            var associationSettings = componentGroupModel.source.macros[macroModel.uid].settings;
                            return getEffectiveValue([associationSettings, macroModel.source.settings], uid, defaultValue);
                        }
                    };

                    componentGroupModel.macros.push(macroModel);
                });

                c.componentGroups.push(componentGroupModel);
            });

            if (c.componentGroups.length === 1) {
                c.setActivePanel(c.componentGroups[0].uid);
            }

            c.panels = status.panels;
            c.panels.push({
                uid: "componentGroups",
                positionIndex: 0,
                viewSource: "views/componentGroupsPanelTemplate.html"
            });

            c.isConfigured = true;
        }

        console.log("Updating UI...");

        $.each(c.componentGroups, (i, componentGroupModel) => {
            var updatedComponentGroup = status.componentGroups.find(g => g.uid === componentGroupModel.uid);
            if (updatedComponentGroup === undefined) {
                return;
            }

            c.configureComponentGroup(componentGroupModel, updatedComponentGroup, status);
        });

        c.notifications = status.notifications;

        importChanges(c.globalVariables, status.global_variables);

        c.isInitialized = true;
    };

    c.configureMacro = function (model, source, componentGroupModel) {
        model.source = source;

        model.viewSource = getValue(source.configuration, "app.view_source", null);
        if (model.viewSource === undefined || model.viewSource === null) {
            model.viewSource = "views/viewMissingTemplateView.html";
        }

        var associationSettings = componentGroupModel.source.macros[model.uid].settings;
        model.sortValue = getEffectiveValue([associationSettings, source.settings], "app.position_index", model.uid);
    };

    c.configureComponentGroup = function (model, source, status) {
        model.source = source;

        importChanges(model.settings, source.settings);

        model.sortValue = getValue(model.settings, "app.position_index", model.uid);

        // Sort the components by its sort value. Do not use sorting in Angular because the
        // actual is required for other code.
        model.components.sort(function (x, y) { return x.sortValue - y.sortValue; });

        $.each(model.components,
            function (i, componentModel) {
                var componentStatus = status.components.find(x => x.uid === componentModel.uid);
                if (componentStatus === undefined) {
                    return;
                }

                c.configureComponent(componentModel, componentStatus, model);
            });
    };

    c.configureComponent = function (model, source, componentGroupModel) {
        model.source = source;

        importChanges(model.settings, source.settings);
        importChanges(model.status, source.status);
        importChanges(model.configuration, source.configuration);

        if (model.viewSource === undefined || model.viewSource === null) {
            model.viewSource = getValue(model.configuration, "app.view_source", null);
            if (model.viewSource === undefined || model.viewSource === null) {
                model.viewSource = "views/viewMissingTemplateView.html";
            }
        }

        var associationSettings = componentGroupModel.source.components[model.uid].settings;
        model.sortValue = getEffectiveValue([associationSettings, model.settings], "app.position_index", model.uid);
    };

    c.moveComponent = function (component, componentGroup, direction) {

        var itemIndex = componentGroup.components.indexOf(component);

        if (direction == "down") {
            if (itemIndex == componentGroup.components.length - 1) {
                return;
            }

            [componentGroup.components[itemIndex], componentGroup.components[itemIndex + 1]] = [componentGroup.components[itemIndex + 1], componentGroup.components[itemIndex]];
        }
        else if (direction == "up") {
            if (itemIndex == 0) {
                return;
            }

            [componentGroup.components[itemIndex], componentGroup.components[itemIndex - 1]] = [componentGroup.components[itemIndex - 1], componentGroup.components[itemIndex]];
        }

        $.each(componentGroup.components,
            function (i, component) {
                c.componentService.setPositionIndex(component.uid, componentGroup.uid, i);
            });
    };

    $http.get("version.txt").then(function (response) {
        c.version = response.data;
    });

    componentService.componentUpdatedCallback = c.applyNewComponentStatus;

    // Start the polling loop for new status.
    apiService.newStatusReceivedCallback = c.applyNewStatus;
    apiService.pollStatus();
}

function getEffectiveValue(sourceList, name, defaultValue) {
    var value = null;
    $.each(sourceList, (i, source) => {
        value = getValue(source, name, null);
        if (value !== null) {
            return false; // Break the loop.
        }
    });

    if (value !== null) {
        return value;
    }

    return defaultValue;
}

function getValue(source, name, defaultValue) {
    if (source === undefined || source === null) {
        return defaultValue;
    }

    if (!source.hasOwnProperty(name)) {
        return defaultValue;
    }

    return source[name];
}

function importChanges(target, source) {
    $.each(source, function (key) {
        var newValue = source[key];

        if (!target.hasOwnProperty(key)) {
            target[key] = newValue;
            return;
        }

        var oldValue = target[key];

        if (angular.toJson(newValue) === angular.toJson(oldValue)) {
            return;
        }

        if (newValue === oldValue) {
            return;
        }

        target[key] = newValue;

        console.log("Updated '" + key + "' from '" + oldValue + "' to '" + newValue + "'.")
    });
}