using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace GoPro.Core.Http
{
	public class Request : IDisposable
	{
		public Url Url;

		public Action Action = (Action)1;

		public Dictionary<string, string> Headers;

		public string Body;

		public RequestPriority Priority = (RequestPriority)1;

		public int Retries = 0;

		public int TimeoutMilliseconds = 0;

		public Timeouts HttpTimeouts;

		public Request()
		{
			//IL_0007: Expected O, but got I4
			//IL_000e: Expected O, but got I4
			Headers = new Dictionary<string, string>();
			Body = "";
			HttpTimeouts = new Timeouts();
		}

		private void _007ERequest()
		{
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007ERequest();
			}
			else
			{
				base.Finalize();
			}
		}

		public sealed override void Dispose()
		{
			Dispose(A_0: true);
			GC.SuppressFinalize(this);
			GC.KeepAlive(this);
		}
	}
}
