function _updateLoadingMessage(message) {
  $('#loadingScreen .spinner-message').html(message);
}

function _showLoading() {
  $("#loadingScreen").show();
  _updateLoadingMessage("Sending, please wait ...");
}

function _updateQuarantine(resource, flag) {
  var csrf_value = $('meta[name=_csrf_token]').attr('content');
  let body = {
    "id": `${resource}`,
    "in_quarantine": flag,
    "_csrf_token": csrf_value
  };
  let promise = new Promise((resolve, reject) => {
    $.ajax({
      url: '/api/action/hdx_qa_resource_patch',
      type: 'POST',
      data: body,
      headers: hdxUtil.net.getCsrfTokenAsObject(),
      success: function (result) {
        if (result.success) {
          resolve(result);
        } else {
          reject(result);
        }
      },
      error: function (result) {
        reject(result);
      }
    });
  });
  return promise;
}

function _updateBrokenLink(resource, flag) {
  var csrf_value = $('meta[name=_csrf_token]').attr('content');
  let body = {
    "id": `${resource}`,
    "broken_link": `${flag}`,
    "_csrf_token": csrf_value
  };
  let promise = new Promise((resolve, reject) => {
    $.ajax({
      url: '/api/action/hdx_mark_broken_link_in_resource',
      type: 'POST',
      data: body,
      headers: hdxUtil.net.getCsrfTokenAsObject(),
      success: function (result) {
        if (result.success) {
          resolve(result);
        } else {
          reject(result);
        }
      },
      error: function (result) {
        reject(result);
      }
    });
  });
  return promise;
}

function _updateAllResourcesKeyValue(package,key,value) {
  var csrf_value = $('meta[name=_csrf_token]').attr('content');
  let body = {
    "id": `${package}`,
    "key": key,
    "value": value,
    "_csrf_token": csrf_value
  };

  let promise = new Promise((resolve, reject) => {
    $.ajax({
      url: '/api/action/hdx_qa_package_revise_resource',
      type: 'POST',
      data: body,
      headers: hdxUtil.net.getCsrfTokenAsObject(),
      success: function (result) {
        if (result.success) {
          resolve(result);
        } else {
          reject(result);
        }
      },
      error: function (result) {
        reject(result);
      }
    });
  });
  return promise;
}

function _getPackageResourceList(elementId) {
  return JSON.parse($(elementId).html());
}

function _getPackageResourceIdList(elementId) {
  return _getPackageResourceList(elementId).map((resource) => resource.id);
}

function updateAllResourcesQuarantine(package,value) {
  _showLoading();
  _updateAllResourcesKeyValue(package,'in_quarantine',value)
    .then(() => {
        _updateLoadingMessage("QA quarantine status successfully updated! Reloading page ...");
    })
    .catch(() => {
        alert("Error, QA quarantine status not updated!");
        $("#loadingScreen").hide();
    })
    .finally(() => {
      location.reload();
    });
}

function viewPIIResults(url) {
  $.get(`${url}?noredirect=true`)
    .done((result)=> {
      console.log(result);
      const visWidgetId = '#qa-results-visualisation';
      const visUrl = 'https://ocha-dap.github.io/dlp-output-viz/';
      const dataUrl = encodeURIComponent(result);
      $(visWidgetId+"-iframe").attr('src', `${visUrl}?dataUrl=${dataUrl}`);
      showOnboardingWidget(visWidgetId);
    });
}

function updateQuarantine(resource, flag) {
  _showLoading();
  _updateQuarantine(resource, flag)
    .then(
      (resolve) => {
        _updateLoadingMessage("Quarantine status successfully updated! Reloading page ...");
      },
      (error) => {
        alert("Error, quarantine status not updated! " + extraMsg);
        $("#loadingScreen").hide();
      }
    )
    .finally(() => {
      location.reload();
    });
}

function updateBrokenLink(resource, flag) {
  _showLoading();
  _updateBrokenLink(resource, flag)
    .then(
      (resolve) => {
        _updateLoadingMessage("Broken link status successfully updated! Reloading page...");
      },
      (error) => {
        alert("Error, broken link status not updated! " + extraMsg);
        $("#loadingScreen").hide();
      }
    )
    .finally(() => {
      location.reload();
    });
}

function updateQuarantineList(resourceListId, flag) {
  _showLoading();
  let resources = _getPackageResourceIdList(resourceListId);
  let resourcesPromise = resources.reduce((currentPromise, resource) => {
    return currentPromise
      .then(() => {
        _updateLoadingMessage(`Updating resource with id [${resource}], please wait ...`);
        return _updateQuarantine(resource, flag);
      })
  }, Promise.resolve([]));

  resourcesPromise
    .then(values => {
      _updateLoadingMessage("Quarantine status successfully updated for all resources! Reloading page ...");
    })
    .catch(errors => {
      alert("Error, quarantine status not updated for at least one resource!");
    })
    .finally(() => {
      location.reload();
    });
}

function qaPackageDetailsSelect(target) {
  $('.qa-package-details').hide();
  $('.qa-package-item.open').removeClass('open');
  $(target).addClass('open');
  let package_id = $(target).attr('data-package-id');
  window.location.hash = `qa-pkg-id-${package_id}`;
  $(`#qa-package-details-${package_id}`).show();
}

function _updateResourceConfirmState(resource, flag, score, piiReportId) {
  let body = {
    "id": `${resource}`,
    "pii_is_sensitive": flag,
  };

  let promise = new Promise((resolve, reject) => {
    const mixpanelPromise = hdxUtil.analytics.sendQADashboardEvent(resource,flag,score,piiReportId);
    const patchPromise = $.ajax({
      url: '/api/action/hdx_qa_resource_patch',
      type: 'POST',
      data: body,
      headers: hdxUtil.net.getCsrfTokenAsObject(),
    });

    mixpanelPromise.then((mixpanelResults) => {
      patchPromise
        .done((result) => {
          if (result.success) {
            resolve(result);
          } else {
            reject(result);
          }
        })
        .fail((result) => {
          reject(result);
        });
    });
  });
  return promise;
}

$(document).ready(() => {
  $(".qa-package-item").on("click", (ev) => qaPackageDetailsSelect(ev.currentTarget));
  let hash = window.location.hash ? window.location.hash.substr(1) : null;
  let pkgId = (hash && hash.startsWith('qa-pkg-id-')) ? hash.substr(10) : null;
  const $target = (pkgId && $('.qa-package-item[data-package-id="' + pkgId + '"]').length) ? $('.qa-package-item[data-package-id="' + pkgId + '"]')[0] : $('.qa-package-item')[0];
  qaPackageDetailsSelect($target);
  if ($target.length) {
    $target.scrollIntoView();
  }
});
