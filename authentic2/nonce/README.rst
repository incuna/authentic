Nonce are value which should be used only once for a certain period or
eventually forever. The nonce application allows any Django application to
implement this behaviour, by taking care of the storage implementation to keep around invalidated nonce.

For nonce which should not be kept forever the application also provide a
cleanup_nonce() function to delete the no longer invalid nonces.
