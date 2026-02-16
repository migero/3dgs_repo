using System;
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace GoPro.Controls
{
	public class ScrubberModel : INotifyPropertyChanged
	{
		public delegate void TimeUpdatedDelegate(ulong mCurrentTimeUs, ulong mDurationUs);

		public delegate void BufferStartedDelegate();

		public delegate void BufferProgressedDelegate(double mBuffer);

		public delegate void BufferStoppedDelegate();

		public TimeUpdatedDelegate TimeUpdated;

		public BufferStartedDelegate BufferStarted;

		public BufferProgressedDelegate BufferProgressed;

		public BufferStoppedDelegate BufferStopped;

		private double mBuffer;

		private ScrubberStatus mStatus;

		private ulong mDurationUs;

		private ulong mCurrentTimeUs;

		public double Buffer
		{
			get
			{
				return mBuffer;
			}
			set
			{
				mBuffer = Math.Min(Math.Max(value, 0.0), 1.0);
				if (BufferProgressed != null)
				{
					BufferProgressed(mBuffer);
				}
				if (mBuffer == 1.0)
				{
					Status = ScrubberStatus.READY;
				}
				else if (mStatus != 0)
				{
					Status = ScrubberStatus.BUFFERING;
				}
				OnPropertyChanged("Buffer");
			}
		}

		public ScrubberStatus Status
		{
			get
			{
				return mStatus;
			}
			private set
			{
				if (mStatus != value)
				{
					mStatus = value;
					if (mStatus == ScrubberStatus.BUFFERING && BufferStarted != null)
					{
						BufferStarted();
					}
					else if (mStatus == ScrubberStatus.READY && BufferStopped != null)
					{
						BufferStopped();
					}
					OnPropertyChanged("Status");
				}
			}
		}

		public ulong DurationUs
		{
			get
			{
				return mDurationUs;
			}
			set
			{
				mDurationUs = value;
				OnPropertyChanged("DurationUs");
			}
		}

		public ulong CurrentTimeUs
		{
			get
			{
				return mCurrentTimeUs;
			}
			set
			{
				if (mCurrentTimeUs != value)
				{
					mCurrentTimeUs = Math.Min(Math.Max(value, 0uL), mDurationUs);
					Status = ScrubberStatus.READY;
					if (TimeUpdated != null)
					{
						TimeUpdated(mCurrentTimeUs, mDurationUs);
					}
					OnPropertyChanged("CurrentTimeUs");
				}
			}
		}

		public event PropertyChangedEventHandler PropertyChanged;

		public ScrubberModel()
		{
			mBuffer = 0.0;
			mCurrentTimeUs = 0uL;
			mDurationUs = 0uL;
			mStatus = ScrubberStatus.BUFFERING;
		}

		private void OnPropertyChanged([CallerMemberName] string name = null)
		{
			this.PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(name));
		}
	}
}
