import React, { useState } from "react";
import { Button, Dialog } from "@/components";

export const useConfirm = (
  title: string,
  message: string
): [() => React.JSX.Element, () => Promise<boolean>] => {
  const [promise, setPromise] = useState<{
    resolve: (value: boolean) => void;
  } | null>(null);

  const confirm = () =>
    new Promise<boolean>((resolve) => {
      setPromise({ resolve });
    });

  const handleClose = () => {
    setPromise(null);
  };

  const handleConfirm = () => {
    promise?.resolve(true);
    handleClose();
  };

  const handleCancel = () => {
    promise?.resolve(false);
    handleClose();
  };

  const ConfirmDialog = () => (
    <Dialog
      isOpen={promise !== null}
      onClose={handleCancel}
      title={title}
      size="sm"
      footer={
        <>
          <Button onClick={handleCancel} type="button" variant="outline">
            Cancel
          </Button>
          <Button onClick={handleConfirm} type="button">
            Confirm
          </Button>
        </>
      }
    >
      <p className="text-sm text-muted-foreground">{message}</p>
    </Dialog>
  );

  return [ConfirmDialog, confirm];
};
