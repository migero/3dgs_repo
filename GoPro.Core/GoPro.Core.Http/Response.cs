using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;

namespace GoPro.Core.Http
{
	public class Response : IDisposable
	{
		public int statusCode;

		public Dictionary<string, string> headers;

		public string body;

		public Response()
		{
			headers = new Dictionary<string, string>();
			body = "";
		}

		private void _007EResponse()
		{
		}

		protected virtual void Dispose([MarshalAs(UnmanagedType.U1)] bool A_0)
		{
			if (A_0)
			{
				_007EResponse();
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
