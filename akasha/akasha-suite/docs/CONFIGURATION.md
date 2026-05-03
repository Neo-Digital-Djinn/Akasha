# Configuration

The suite assumes:

- Repos live under `~/`
- Akasha repos use GitHub username `mythologyprospector-hub`
- SSH host alias `github-akasha` exists in `~/.ssh/config`

Example SSH config:

```ssh
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
  IdentitiesOnly yes

Host github-akasha
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519_akasha
  IdentitiesOnly yes
```
