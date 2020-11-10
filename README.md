# ena-upload-wrapper
Galaxy wrapper for ena-cli-upload

This tool is shipped in a ready to use Galaxy container found [here](https://github.com/ELIXIR-Belgium/ena-upload-container).

## Set up user credentials on Galaxy

To enable users to set their credentials for this tool,
make sure the file `config/user_preferences_extra_conf.yml` has the following section:

```
    ena_account:
        description: Your ENA Brokering account details
        inputs:
            - name: webin_id
              label: webin_id
              type: text
              required: False
            - name: password
              label: Password
              type:  password
              required: False
```
