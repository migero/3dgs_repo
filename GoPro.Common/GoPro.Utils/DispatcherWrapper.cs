using System;
using System.Windows.Threading;

namespace GoPro.Utils
{
	public class DispatcherWrapper : IDispatcher
	{
		private Dispatcher mDispatcher;

		public DispatcherWrapper(Dispatcher dispatcher)
		{
			mDispatcher = dispatcher;
		}

		public void Invoke(Action callback)
		{
			mDispatcher.Invoke(callback);
		}

		public void InvokeAsync(Action callback)
		{
			mDispatcher.InvokeAsync(callback);
		}
	}
}
