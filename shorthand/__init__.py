from shorthand.utils.config import get_notes_config, write_config, \
    modify_config


class ShorthandServer(object):
    '''Main Shorthand Server API
       This implementation exposes a nicer API than calling
       the underlying functions directly and manages basic
       configuration transparently
    '''

    def __init__(self, config_path):
        '''Initialize the server with the configuration
           in the specified file
        '''
        # super(ShorthandServer, self).__init__()
        self.config_path = config_path
        self.reload_config()

    # -------------------------
    # --- Config Management ---
    # -------------------------
    def get_config(self):
        '''Get the current server configuration
        '''
        return self.config

    def reload_config(self):
        '''Reload the config from the config file
        '''
        self.config = get_notes_config(self.config_path)

    def update_config(self, updates):
        '''Update one or more fields in the configuration
           Note: This does not save the updated config to disk
        '''
        self.config = modify_config(self.config, updates)

    def save_config(self):
        '''Save the current config to the config file
        '''
        write_config(self.config_path, self.config)

    def check_config_init(self):
        '''Validate that config is present
        '''
        if not self.config:
            raise ValueError('Shorthand Server is not yet '
                             'initialized with config')

    # -------------
    # --- Todos ---
    # -------------
    def get_todos(self):
        pass
