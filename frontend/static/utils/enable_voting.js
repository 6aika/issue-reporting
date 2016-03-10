// Voting. Do a POST request to record the vote.
// Voting is attached to feedback_list_vote_icon element.
function enable_voting(csrf_token_string, voting_url_string) {
    $("body").on("click", ".feedback_list_vote_icon", function () {
        var id = $(this).attr("id");
        var data = {id: id, csrfmiddlewaretoken: csrf_token_string};
        $.post(voting_url_string, data, function (data) {
            if (data.status === "success") {
                var value = parseInt($(this).next().text()) + 1;
                $(this).next().text(value);
                $.notify({
                    message: data.message
                }, {
                    type: "success"
                });
            }
            else {
                $.notify({
                    message: data.message
                }, {
                    type: "danger"
                });
            }
        }.bind(this));
    });
}