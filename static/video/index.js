$(function() {
    // Get handle to the chat div 
    var $chatWindow = $('#messages');

    // Our interface to the Chat service
    var chatClient;

    // A handle to the "general" chat channel - the one and only channel we
    // will have in this sample app
    var generalChannel;

    // The server will assign the client a random username - store that value
    // here
    var username;

    // Helper function to print info messages to the chat window
    function print(infoMessage, asHtml) {
        var $msg = $('<div class="modal-body">');
        if (asHtml) {
            $msg.html(infoMessage);
        } else {
            $msg.text(infoMessage);
        }
        $chatWindow.append($msg);
    }

    // Helper function to print chat message to the chat window
    function printMessage(fromUser, message) {
        var $user = $('<li class="media m-b-md">');
        if (fromUser === username) {
            $user.addClass('media-current-user');
        } else {
            $user.addClass('media-left');
        }
        var $message = $('<div class="media-body-text">').html(message);
        var $container = $('<div class="media-body">');
        ($user).append($container).append($message);
        $chatWindow.append($user);
        console.log($container)
        $chatWindow.scrollTop($chatWindow[0].scrollHeight);
    }

    // Alert the user they have been assigned a random username
    print('Logging in...');

    // Get an access token for the current user, passing a username (identity)
    // and a device ID - for browser-based apps, we'll always just use the 
    // value "browser"
    $.getJSON('/token', {
        device: 'browser'
    }, function(data) {
        // Alert the user they have been assigned a random username
        username = data.identity;
        print('Your username is: ' 
            + '<span class="me">' + username + '</span>', true);

        // Initialize the Chat client
        chatClient = new Twilio.Chat.Client(data.token);
        chatClient.getSubscribedChannels().then(createOrJoinGeneralChannel);        
    });

    function createOrJoinGeneralChannel() {
        // Get the general chat channel, which is where all the messages are
        // sent in this simple application
        print('Attempting to join "One-on-one" chat channel...');
        var promise = chatClient.getChannelByUniqueName('two-on-two');
        promise.then(function(channel) {
            generalChannel = channel;
            console.log('Found one-on-one channel:');
            console.log(generalChannel);
            setupChannel();
        }).catch(function() {
            // If it doesn't exist, let's create it
            console.log('Creating general channel');
            chatClient.createChannel({
                uniqueName: 'two-on-two',
                friendlyName: 'One-on-one Chat Channel'
            }).then(function(channel) {
                console.log('Created one-on-one channel:');
                console.log(channel);
                generalChannel = channel;
                setupChannel();
            });
        });
    }

    // Set up channel after it has been found
    function setupChannel() {
        // Join the general channel
        generalChannel.join().then(function(channel) {
            print('Joined channel as ' 
                + '<span class="me">' + username + '</span>.', true);
        });

        // Listen for new messages sent to the channel
        generalChannel.on('messageAdded', function(message) {
            printMessage(message.author, message.body);
        });
    }

    // Send a new message to the general channel
    var $input = $('#chat-input');
    $input.on('keydown', function(e) {
        if (e.keyCode == 13 && generalChannel) {
            generalChannel.sendMessage($input.val())
            $input.val('');
        }
    });
});