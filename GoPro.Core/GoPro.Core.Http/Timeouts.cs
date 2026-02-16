namespace GoPro.Core.Http
{
	public class Timeouts
	{
		private int mResolveTimeout = 0;

		private int mConnectTimeout = 60000;

		private int mSendTimeout = 30000;

		private int mReceiveTimeout = 30000;

		public int ReceiveTimeout
		{
			get
			{
				return mReceiveTimeout;
			}
			set
			{
				mReceiveTimeout = value;
			}
		}

		public int SendTimeout
		{
			get
			{
				return mSendTimeout;
			}
			set
			{
				mSendTimeout = value;
			}
		}

		public int ConnectTimeout
		{
			get
			{
				return mConnectTimeout;
			}
			set
			{
				mConnectTimeout = value;
			}
		}

		public int ResolveTimeout
		{
			get
			{
				return mResolveTimeout;
			}
			set
			{
				mResolveTimeout = value;
			}
		}

		public Timeouts(int resolve, int connect, int send, int receive)
		{
			mResolveTimeout = resolve;
			mConnectTimeout = connect;
			mSendTimeout = send;
			mReceiveTimeout = receive;
		}

		public Timeouts()
		{
		}
	}
}
