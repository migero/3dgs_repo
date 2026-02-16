using System;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class StorePurchaseResultContainer
	{
		public StorePurchaseStatus Status { get; }

		public Exception ExtendedError { get; }

		public StorePurchaseResultContainer(StorePurchaseStatus status, Exception extendedError = null)
		{
			//IL_0007: Unknown result type (might be due to invalid IL or missing references)
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			Status = status;
			ExtendedError = extendedError;
		}

		public StorePurchaseResultContainer(StorePurchaseResult result)
		{
			//IL_0008: Unknown result type (might be due to invalid IL or missing references)
			//IL_000d: Unknown result type (might be due to invalid IL or missing references)
			Status = result.get_Status();
			ExtendedError = result.get_ExtendedError();
		}
	}
}
