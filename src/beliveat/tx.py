# -*- coding: utf-8 -*-

"""Provides a ``join_to_transaction`` function which adds a function call,
  with args / kwargs, as an after commit hook.
"""

import logging
logger = logging.getLogger(__name__)

import transaction

def _handle_commit(tx_succeeded, *args_list, **kwargs):
    """Handle a successful commit by calling the callable registered as an after
      commit hook.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_callable = Mock()
          >>> mock_args_list = [mock_callable, 'a', 'b']
      
      If the transaction didn't succeed, it's a noop::
      
          >>> _handle_commit(False)
          >>> mock_callable.called = False
      
      Otherwise treats the first item in the ``args_list`` as the callable
      and calls it with the remaining args and the kwargs::
      
          >>> _handle_commit(True, *mock_args_list, foo='bar')
          >>> mock_callable.assert_called_with('a', 'b', foo='bar')
      
    """
    
    # If in debug mode, show what's going on under the hood.
    log_args = (tx_succeeded, args_list, kwargs)
    logger.debug('handle_commit: {0} for {1} {2}'.format(*log_args))
    
    # If the transaction succeeded, call the callable.
    if tx_succeeded:
        callable_ = args_list[0]
        args = args_list[1:]
        callable_(*args, **kwargs)

def join_to_transaction(callable_, *args, **kwargs):
    """Add an after commit hook to the current transaction to call 
      ``callable_(*args, **kwargs)`` iff the current transaction succeeds.
      
      Setup::
      
          >>> from mock import Mock
          >>> import transaction
          >>> _original_get = transaction.get
          >>> transaction.get = Mock()
          >>> mock_tx = Mock()
          >>> transaction.get.return_value = mock_tx
      
      Add an after commit hook to the current transaction::
      
          >>> join_to_transaction('callable', 'a', 'b', foo='bar')
          >>> mock_tx.addAfterCommitHook.assert_called_with(_handle_commit, 
          ...         args=['callable', 'a', 'b'], kws={'foo': 'bar'})
      
      Teardown::
      
          >>> transaction.get = _original_get
      
    """
    
    # If in debug mode, show what's going on under the hood.
    log_args = (callable_, args, kwargs)
    logger.debug('join_to_transaction: {0} {1} {2}'.format(*log_args))
    
    # Build a args list of [callable_, *args]
    args_list = [callable_]
    args_list.extend(args)
    
    # Add an after commit hook.
    current_tx = transaction.get()
    current_tx.addAfterCommitHook(_handle_commit, args=args_list, kws=kwargs)

