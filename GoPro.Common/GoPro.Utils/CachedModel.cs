using System;
using System.Collections.Generic;

namespace GoPro.Utils
{
	public class CachedModel<T> where T : new()
	{
		public T Data;

		private Stack<T> mSnapshots;

		public event Action SnapshotRestored;

		public event Action SnapshotCreated;

		public event Action SnapshotCleared;

		public CachedModel()
		{
			Data = new T();
			mSnapshots = null;
		}

		public CachedModel(T model)
		{
			Data = model.DeepCopy();
			mSnapshots = null;
		}

		public void PushSnapshot()
		{
			if (mSnapshots == null)
			{
				mSnapshots = new Stack<T>();
			}
			T item = Data.DeepCopy();
			mSnapshots.Push(item);
			this.SnapshotCreated?.Invoke();
		}

		public void PopSnapshot()
		{
			if (mSnapshots.Count > 0)
			{
				Data = mSnapshots.Pop();
				this.SnapshotRestored?.Invoke();
			}
		}

		public void ClearSnapshots()
		{
			mSnapshots = null;
			this.SnapshotCleared?.Invoke();
		}

		public bool HasSnapshots()
		{
			if (mSnapshots != null)
			{
				return mSnapshots.Count > 0;
			}
			return false;
		}

		public void RestoreBottomSnapshot()
		{
			if (mSnapshots != null && mSnapshots.Count != 0)
			{
				Data = (T)mSnapshots.ToArray().GetValue(0);
				mSnapshots = null;
				this.SnapshotRestored?.Invoke();
			}
		}

		public void ResetData()
		{
			Data = new T();
			this.SnapshotRestored?.Invoke();
		}

		public T CloneData()
		{
			return Data.DeepCopy();
		}
	}
}
