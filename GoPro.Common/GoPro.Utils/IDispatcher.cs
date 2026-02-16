using System;

namespace GoPro.Utils
{
	public interface IDispatcher
	{
		void Invoke(Action callback);

		void InvokeAsync(Action callback);
	}
}
