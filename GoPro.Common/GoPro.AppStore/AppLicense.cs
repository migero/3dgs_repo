using System;
using Windows.Services.Store;

namespace GoPro.AppStore
{
	public class AppLicense
	{
		private StoreAppLicense mStoreApplicense;

		public string SkuStoreID => mStoreApplicense.get_SkuStoreId();

		public DateTimeOffset Expiration => mStoreApplicense.get_ExpirationDate();

		public bool IsActive => mStoreApplicense.get_IsActive();

		public bool IsDiscLicense => mStoreApplicense.get_IsDiscLicense();

		public bool IsTrial => mStoreApplicense.get_IsTrial();

		public bool IsTrialOwnedByUser => mStoreApplicense.get_IsTrialOwnedByThisUser();

		public TimeSpan TrialTimeRemaining => mStoreApplicense.get_TrialTimeRemaining();

		public string TrailUniqueID => mStoreApplicense.get_TrialUniqueId();

		public AppLicense(StoreAppLicense storeAppLicense)
		{
			mStoreApplicense = storeAppLicense;
		}
	}
}
